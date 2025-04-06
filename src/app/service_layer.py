import random
import py_avataaars as pa  # type: ignore
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from functools import partial
from typing import List, Optional, Dict, Sequence, Set, Tuple, Union, Any, cast

from sqlmodel import Session, select
from mutagen.id3 import USLT  # type: ignore

from src.app import dto

from . import database as db
from . import db_helpers
from .utils import get_audio_object, AudioType


class RequestType(Enum):
    RANDOM = 1
    NEWEST = 2
    HIGHEST = 3
    FREQUENT = 4
    RECENT = 5
    BY_NAME = 6
    BY_ARTIST = 7
    BY_YEAR = 8
    BY_GENRE = 9


def fill_artist(
    db_artist: db.Artist,
    db_user: db.User | None,
    with_albums: bool = True,
    with_songs: bool = False,
) -> dto.Artist:
    result = dto.Artist(
        id=db_artist.id,
        name=db_artist.name,
        artist_image_url=None,
        starred=None,
    )
    if with_albums:
        result.albums = fill_albums(db_artist.albums, None, with_songs=with_songs)
    return result


def fill_album(
    db_album: db.Album, db_user: db.User | None, with_songs: bool = False
) -> dto.Album:
    album_genres: List[db.Genre] = list(get_album_genres(db_album))
    album = dto.Album(
        id=db_album.id,
        name=db_album.name,
        song_count=db_album.total_tracks,
        duration=get_tracklist_duration(db_album.tracks),
        created=datetime.now(),
        artist=join_artist_names(db_album.artists),
        artist_id=get_album_artist_id_by_album(db_album),
        cover_art_id=db_album.id,
        play_count=db_album.play_count,
        starred=None,
        year=extract_year(db_album.year),
        genre=join_genre_names(album_genres),
        artists=fill_artist_items(db_album.artists),
        genres=fill_genre_items(album_genres),
    )
    if with_songs:
        album.tracks = fill_tracks(db_album.tracks, db_user)
    return album


def fill_albums(
    db_albums: Sequence[db.Album],
    db_user: db.User | None,
    with_songs: bool,
    need_sort: bool = True,
) -> List[dto.Album]:
    if not need_sort:
        return list(
            map(
                partial(fill_album, db_user=db_user, with_songs=with_songs),
                db_albums,
            ),
        )
    return list(
        sorted(
            map(partial(fill_album, db_user=db_user, with_songs=with_songs), db_albums),
            key=lambda album: album.id,
        )
    )


def fill_artist_item(artist: db.Artist) -> dto.ArtistItem:
    return dto.ArtistItem(
        id=artist.id,
        name=artist.name,
    )


def fill_artist_items(artists: Sequence[db.Artist]) -> List[dto.ArtistItem]:
    return list(sorted(map(fill_artist_item, artists), key=lambda artist: artist.id))


def fill_genre_item(genre: db.Genre) -> dto.GenreItem:
    return dto.GenreItem(
        name=genre.name,
    )


def fill_genre_items(genres: Sequence[db.Genre]) -> List[dto.GenreItem]:
    return list(sorted(map(fill_genre_item, genres), key=lambda genre: genre.name))


def set_track_starred(db_track: db.Track, db_user: db.User | None) -> datetime | None:
    if db_user is None:
        return None
    for track in db_track.track_favourites:
        if track.user_id == db_user.id:
            return datetime.fromisoformat(track.added_at)
    return None


def fill_track(db_track: db.Track, db_user: db.User | None) -> dto.Track:
    return dto.Track(
        id=db_track.id,
        title=db_track.title,
        album=db_track.album.name,
        album_id=db_track.album_id,
        artist=join_artist_names(db_track.artists),
        artist_id=get_album_artist_id_by_artist(get_album_artist(db_track)),
        track_number=db_track.album_position,
        disc_number=None,
        year=extract_year(db_track.year),
        genre=join_genre_names(db_track.genres),
        cover_art_id=db_track.id,
        file_size=db_track.file_size,
        content_type=db_track.type,
        duration=int(db_track.duration),
        bit_rate=int(round(db_track.bit_rate / 1024)),
        sampling_rate=db_track.sample_rate,
        bit_depth=db_track.bits_per_sample,
        channel_count=db_track.channels,
        path=db_track.file_path,
        play_count=db_track.plays_count,
        created=datetime.now(),
        starred=set_track_starred(db_track, db_user),
        bpm=None,
        comment=None,
        artists=fill_artist_items(db_track.artists),
        genres=fill_genre_items(db_track.genres),
    )


def fill_tracks(
    db_tracks: Sequence[db.Track], db_user: db.User | None
) -> List[dto.Track]:
    return list(
        sorted(
            map(partial(fill_track, db_user=db_user), db_tracks),
            key=lambda track: track.id,
        )
    )


def fill_genre(db_genre: db.Genre) -> dto.Genre:
    albumCount = len(set([t.album_id for t in db_genre.tracks]))
    songCount = len(db_genre.tracks)
    return dto.Genre(albumCount=albumCount, songCount=songCount, name=db_genre.name)


def fill_genres(db_genres: Sequence[db.Genre]) -> List[dto.Genre]:
    return list(sorted(map(fill_genre, db_genres), key=lambda genre: genre.name))


def fill_artists(
    db_artists: Sequence[db.Artist],
    db_user: db.User | None,
    with_albums: bool = True,
    with_songs: bool = False,
) -> List[dto.Artist]:
    return list(
        sorted(
            map(
                partial(
                    fill_artist,
                    db_user=db_user,
                    with_albums=with_albums,
                    with_songs=with_songs,
                ),
                db_artists,
            ),
            key=lambda artist: artist.id,
        )
    )


def fill_playlist(
    db_playlist: db.Playlist, db_user: db.User | None, with_songs: bool = False
) -> dto.Playlist:
    now = datetime.now()
    playlist = dto.Playlist(
        id=db_playlist.id,
        name=db_playlist.name,
        song_count=db_playlist.total_tracks,
        duration=get_tracklist_duration(
            playlist_tracks_to_tracks(db_playlist.playlist_tracks)
        ),
        created=now,
        changed=now,
        owner=db_playlist.user.login,
        public=True,
    )
    if with_songs:
        playlist.tracks = fill_tracks(
            playlist_tracks_to_tracks(db_playlist.playlist_tracks), db_user
        )
    return playlist


def fill_playlists(
    db_playlists: Sequence[db.Playlist],
    db_user: db.User | None,
    with_songs: bool = False,
) -> List[dto.Playlist]:
    return list(
        sorted(
            map(
                partial(fill_playlist, db_user=db_user, with_songs=with_songs),
                db_playlists,
            ),
            key=lambda playlist: playlist.id,
        )
    )


def get_album_artist_id_by_track(track: db.Track) -> int:
    if track.album_artist_id:
        return track.album_artist_id
    if len(track.artists) > 0:
        return track.artists[0].id
    return -1


def get_album_artist_id_by_album(album: db.Album) -> int:
    if album.album_artist_id:
        return album.album_artist_id
    if len(album.artists) > 0:
        return album.artists[0].id
    return -1


def get_tracklist_duration(db_tracks: Sequence[db.Track]) -> int:
    if len(db_tracks) == 0:
        return 0
    return int(sum([t.duration for t in db_tracks]))


def get_album_genre(db_album: db.Album) -> Optional[str]:
    if len(db_album.tracks) == 0:
        return None
    return join_genre_names(db_album.tracks[0].genres)


def get_album_genres(db_album: db.Album) -> Set[db.Genre]:
    genres: Set[db.Genre] = set()
    if len(db_album.tracks) == 0:
        return genres
    for track in db_album.tracks:
        genres.update(track.genres)
    return genres


class AlbumService:
    def __init__(self, session: Session):
        self.album_db_helper = db_helpers.AlbumDBHelper(session)

    def get_album_by_id(
        self,
        id: int,
        db_user: db.User | None = None,
    ) -> Optional[dto.Album]:
        db_album = self.album_db_helper.get_album_by_id(id)
        if db_album:
            return fill_album(db_album, db_user, with_songs=True)
        return None

    def get_album_list(
        self,
        type: RequestType,
        size: int = 10,
        offset: int = 0,
        from_year: Optional[str] = None,
        to_year: Optional[str] = None,
        genre: Optional[str] = None,
        music_folder_id: Optional[str] = None,
    ) -> Optional[List[dto.Album]]:
        result: Sequence[db.Album] = []
        match type:
            case RequestType.RANDOM:
                albums = self.album_db_helper.get_all_albums()
                result = random.sample(albums, min(size, len(albums)))
            case RequestType.BY_NAME:
                result = list(self.album_db_helper.get_albums_by_name(size, offset))
            case RequestType.BY_ARTIST:
                albums = list(self.album_db_helper.get_all_albums())
                albums.sort(key=lambda album: self.compare_albums_by_artist(album.id))
                result = albums[offset : offset + size]
            case RequestType.BY_YEAR if from_year is not None and to_year is not None:
                min_year: str = min(from_year, to_year)
                max_year: str = max(from_year, to_year)
                reversed_order = from_year > to_year

                result = self.album_db_helper.get_sorted_by_year_albums(
                    min_year, max_year, size, offset, reversed_order
                )
            case RequestType.BY_GENRE if genre is not None:
                result = self.album_db_helper.get_albums_by_genre(genre, size, offset)
            case RequestType.FREQUENT:
                result = self.album_db_helper.get_sorted_albums_by_frequency(
                    size, offset
                )
            case RequestType.NEWEST | RequestType.HIGHEST | RequestType.RECENT:
                raise NotImplementedError()
            case _:  # validation error
                return None

        return fill_albums(result, None, with_songs=False, need_sort=False)

    def compare_albums_by_artist(self, album_id: int) -> str:
        artist: Optional[db.Artist] = self.album_db_helper.get_album_artist(album_id)
        return "" if artist is None else artist.name

    def get_sorted_artist_albums(
        self, artistId: int, size: int = 10, offset: int = 0
    ) -> List[dto.Album]:
        albums = self.album_db_helper.get_sorted_artist_albums(artistId, size, offset)
        return fill_albums(albums, None, with_songs=False)


def join_artist_names(artists: Sequence[db.Artist]) -> Optional[str]:
    if len(artists) == 0:
        return None
    return ", ".join(sorted(a.name for a in artists))


def join_genre_names(genres: Sequence[db.Genre]) -> Optional[str]:
    if len(genres) == 0:
        return None
    return ", ".join(sorted(g.name for g in genres))


def get_album_artist(db_track: db.Track) -> Optional[db.Artist]:
    # TODO MUS-206 Use db_track.album_artist
    if len(db_track.album.artists) > 0:
        return db_track.album.artists[0]
    return None


def get_album_artist_id_by_artist(db_artist: Optional[db.Artist]) -> Optional[int]:
    if db_artist:
        return db_artist.id
    return None


def extract_year(str_year: str | None) -> int | None:
    if str_year and len(str_year) == 4 and str_year.isnumeric():
        return int(str_year)
    return None


class TrackService:
    def __init__(self, session: Session):
        self.track_db_helper = db_helpers.TrackDBHelper(session)
        self.genre_db_helper = db_helpers.GenresDBHelper(session)

    def get_song_by_id(self, id: int, db_user: db.User | None) -> Optional[dto.Track]:
        db_track = self.track_db_helper.get_track_by_id(id)
        if db_track:
            return fill_track(db_track, db_user)
        return None

    def get_songs_by_genre(
        self,
        genre: str,
        count: int = 10,
        offset: int = 0,
        music_folder: str | None = None,
        db_user: db.User | None = None,
    ) -> List[dto.Track]:
        return fill_tracks(
            self.track_db_helper.get_tracks_by_genre_name(genre, count, offset),
            db_user,
        )

    def get_random_songs(
        self,
        size: int = 10,
        genre: Optional[str] = None,
        from_year: Optional[str] = None,
        to_year: Optional[str] = None,
        music_folder_id: Optional[str] = None,
        db_user: db.User | None = None,
    ) -> List[dto.Track]:
        if size < 0:
            return []
        tracks = self.track_db_helper.get_all_tracks()
        if genre:
            tracks = self.track_db_helper.get_tracks_by_genre_name(genre)
        if from_year:
            tracks = list(
                filter(lambda track: track.year and track.year >= from_year, tracks)
            )
        if to_year:
            tracks = list(
                filter(lambda track: track.year and track.year <= to_year, tracks)
            )
        random_tracks = random.sample(tracks, min(size, len(tracks)))
        return fill_tracks(random_tracks, db_user)

    def extract_lyrics(self, id: int) -> Optional[List[Dict[str, Any]]]:
        track = self.track_db_helper.get_track_by_id(id)
        if track:
            audio, audio_type = get_audio_object(track)
            match audio_type:
                case AudioType.MP3:
                    return [
                        {"text": audio[tag].text.splitlines(), "lang": audio[tag].lang}
                        for tag in audio
                        if isinstance(audio[tag], USLT)
                    ]
                case AudioType.FLAC:
                    if audio.tags:
                        return [
                            {"text": tag.splitlines()}
                            for tag in audio.tags.get("lyrics", [])
                        ]
                    return []
        else:
            return None


class GenreService:
    def __init__(self, session: Session):
        self.DBHelper = db_helpers.GenresDBHelper(session)

    def get_genres(self) -> List[dto.Genre]:
        db_genres = self.DBHelper.get_all_genres()
        genres = fill_genres(db_genres)
        return genres


class ArtistService:
    def __init__(self, session: Session):
        self.artist_db_helper = db_helpers.ArtistDBHelper(session)

    @staticmethod
    def join_artists_names(artists: List[db.Artist]) -> str:
        return ", ".join(a.name for a in artists)

    def get_artist_by_id(self, id: int) -> Optional[dto.Artist]:
        db_artist = self.artist_db_helper.get_artist_by_id(id)
        if db_artist:
            return fill_artist(db_artist, None, with_albums=True, with_songs=True)
        return None


class SearchService:
    def __init__(self, session: Session):
        self.artist_db_helper = db_helpers.ArtistDBHelper(session)
        self.album_db_helper = db_helpers.AlbumDBHelper(session)
        self.track_db_helper = db_helpers.TrackDBHelper(session)

    def search2(
        self,
        query: str,
        artist_count: int,
        artist_offset: int,
        album_count: int,
        album_offset: int,
        song_count: int,
        song_offset: int,
        db_user: db.User | None = None,
    ) -> Tuple[Sequence[dto.Artist], Sequence[dto.Album], Sequence[dto.Track]]:

        db_artists = self.artist_db_helper.get_artists(
            artist_count, artist_offset, filter_name=query
        )
        db_albums = self.album_db_helper.get_albums(
            album_count, album_offset, filter_name=query
        )
        db_tracks = self.track_db_helper.get_tracks(
            song_count, song_offset, filter_title=query
        )

        return (
            fill_artists(db_artists, None, with_albums=False, with_songs=False),
            fill_albums(db_albums, None, with_songs=False),
            fill_tracks(db_tracks, db_user),
        )

    def search3(
        self,
        query: str,
        artist_count: int,
        artist_offset: int,
        album_count: int,
        album_offset: int,
        song_count: int,
        song_offset: int,
        db_user: db.User | None = None,
    ) -> Tuple[Sequence[dto.Artist], Sequence[dto.Album], Sequence[dto.Track]]:
        if query != "":
            return self.search2(
                query,
                artist_count,
                artist_offset,
                album_count,
                album_offset,
                song_count,
                song_offset,
                db_user,
            )
        db_artists = self.artist_db_helper.get_all_artists()
        db_albums = self.album_db_helper.get_all_albums()
        db_tracks = self.track_db_helper.get_all_tracks()

        return (
            fill_artists(db_artists, None, with_albums=False, with_songs=False),
            fill_albums(db_albums, None, with_songs=False),
            fill_tracks(db_tracks, db_user),
        )


def playlist_tracks_to_tracks(
    db_playlist_tracks: Sequence[db.PlaylistTrack],
) -> List[db.Track]:
    return [pt.track for pt in db_playlist_tracks]


class StarService:
    def __init__(self, session: Session):
        self.favourite_db_helper = db_helpers.FavouriteDBHelper(session)

    def star(
        self,
        track_ids: Sequence[int],
        album_ids: Sequence[int],
        artist_ids: Sequence[int],
        playlist_ids: Sequence[int],
        user: db.User,
    ) -> None:
        for id in track_ids:
            self.favourite_db_helper.star_track(id, user.id)
        for id in artist_ids:
            self.favourite_db_helper.star_artist(id, user.id)
        for id in album_ids:
            self.favourite_db_helper.star_album(id, user.id)
        for id in playlist_ids:
            self.favourite_db_helper.star_playlist(id, user.id)

    def unstar(
        self,
        track_ids: Sequence[int],
        album_ids: Sequence[int],
        artist_ids: Sequence[int],
        playlist_ids: Sequence[int],
        user: db.User,
    ) -> None:
        for id in track_ids:
            self.favourite_db_helper.unstar_track(id, user.id)
        for id in artist_ids:
            self.favourite_db_helper.unstar_artist(id, user.id)
        for id in album_ids:
            self.favourite_db_helper.unstar_album(id, user.id)
        for id in playlist_ids:
            self.favourite_db_helper.unstar_playlist(id, user.id)

    def get_starred(
        self, user: db.User
    ) -> Tuple[List[dto.Track], List[dto.Album], List[dto.Artist], List[dto.Playlist]]:
        db_tracks = self.favourite_db_helper.get_starred_tracks(user.id)
        db_albums = self.favourite_db_helper.get_starred_albums(user.id)
        db_artists = self.favourite_db_helper.get_starred_artists(user.id)
        db_playlists = self.favourite_db_helper.get_starred_playlists(user.id)

        tracks = fill_tracks(db_tracks, user)
        albums = fill_albums(db_albums, user, with_songs=False)
        artists = fill_artists(db_artists, user, with_albums=False, with_songs=False)
        playlists = fill_playlists(db_playlists, user, with_songs=False)
        return tracks, albums, artists, playlists


class PlaylistService:
    def __init__(self, session: Session):
        self.playlist_db_helper = db_helpers.PlaylistDBHelper(session)

    def create_playlist(
        self, playlist_name: str, track_ids: Sequence[int], user: db.User
    ) -> dto.Playlist:
        db_playlist: db.Playlist = self.playlist_db_helper.create_playlist(
            playlist_name, track_ids, user.id
        )
        return fill_playlist(db_playlist, user, with_songs=True)

    def update_playlist(
        self,
        id: int,
        new_name: str,
        tracks_to_add: Sequence[int],
        tracks_to_remove: Sequence[int],
    ) -> bool:
        playlist = self.playlist_db_helper.update_playlist(
            id, new_name, tracks_to_add, tracks_to_remove
        )
        if playlist:
            return True
        return False

    def delete_playlist(self, id: int, user: db.User) -> bool:
        return self.playlist_db_helper.delete_playlist(id)

    def get_playlist(self, id: int, db_user: db.User | None) -> dto.Playlist | None:
        db_playlist = self.playlist_db_helper.get_playlist(id)
        if db_playlist:
            return fill_playlist(db_playlist, db_user, with_songs=True)
        return None

    def get_playlists(self, db_user: db.User | None) -> List[dto.Playlist]:
        db_playlists = self.playlist_db_helper.get_all_playlists(db_user)
        return fill_playlists(db_playlists, db_user, with_songs=False)


class IndexService:
    def __init__(self, session: Session):
        self.artist_db_helper = db_helpers.ArtistDBHelper(session)
        self.track_db_helper = db_helpers.TrackDBHelper(session)

    def get_indexes_artists(
        self,
        music_folder_id: str = "",
        if_modified_since_ms: int = 0,
        with_childs: bool = False,
    ) -> dto.Indexes:
        indexes: dto.Indexes = dto.Indexes(
            last_modified=datetime.now()
        )  #  TODO MUS-208 fill last_modified
        artists: List[dto.Artist] = fill_artists(
            self.artist_db_helper.get_all_artists(),
            None,
            with_albums=True,
            with_songs=with_childs,
        )
        sorted_artists = sorted(artists, key=lambda a: a.name)

        letter: str = ""
        letter_artists: List[dto.Artist] = []
        for a in sorted_artists:
            if len(a.name) > 0 and a.name[0] != letter:
                if len(letter_artists) > 0:
                    indexes.artist_index.append(dto.ArtistIndex(letter, letter_artists))
                letter = a.name[0]
                letter_artists = []
            letter_artists.append(a)

        if len(letter_artists) > 0:
            indexes.artist_index.append(dto.ArtistIndex(letter, letter_artists))

        if with_childs:
            tracks: Sequence[dto.Track] = fill_tracks(
                self.track_db_helper.get_all_tracks(), None
            )
            indexes.tracks.extend(tracks)

        return indexes


def random_enum_choice(e: type[Enum]) -> Any:
    return random.choice(list(e))


def random_avatar() -> Tuple[bytes, str]:
    avatar = pa.PyAvataaar(
        style=pa.AvatarStyle.CIRCLE,
        skin_color=random_enum_choice(pa.SkinColor),
        hair_color=random_enum_choice(pa.HairColor),
        facial_hair_type=random_enum_choice(pa.FacialHairType),
        facial_hair_color=random_enum_choice(pa.HairColor),
        top_type=random_enum_choice(pa.TopType),
        hat_color=random_enum_choice(pa.Color),
        mouth_type=random_enum_choice(pa.MouthType),
        eye_type=random_enum_choice(pa.EyesType),
        eyebrow_type=random_enum_choice(pa.EyebrowType),
        nose_type=random_enum_choice(pa.NoseType),
        accessories_type=random_enum_choice(pa.AccessoriesType),
        clothe_type=random_enum_choice(pa.ClotheType),
        clothe_color=random_enum_choice(pa.Color),
        clothe_graphic_type=random_enum_choice(pa.ClotheGraphicType),
    )
    png = avatar.render_png()
    return (png, avatar.unique_id)


def generate_and_save_avatar(session: Session, user: db.User) -> bytes:
    avatar, avatar_uid = random_avatar()

    user.avatar = avatar_uid
    session.commit()
    session.refresh(user)

    return avatar


def get_avatar(user: db.User) -> bytes:
    avatar = pa.PyAvataaar()
    avatar.unique_id = user.avatar
    return cast(bytes, avatar.render_png())


def get_user_by_username(session: Session, username: str) -> Optional[db.User]:
    user_helper = db_helpers.UserDBHelper(session)
    return user_helper.get_user_by_username(username)


def create_user(
    session: Session, username: str, password: str
) -> Tuple[None, Optional[str]]:
    login_exists = session.exec(
        select(db.User).where(db.User.login == username)
    ).one_or_none()

    if login_exists:
        return (None, "Login already exists")

    _, avatar_uid = random_avatar()
    session.add(db.User(login=username, password=password, avatar=avatar_uid))
    session.commit()
    return (None, None)


def create_default_user() -> None:
    with Session(db.engine) as session:
        create_user(session, "admin", "admin")
