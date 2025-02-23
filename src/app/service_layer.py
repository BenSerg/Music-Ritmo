import random
import py_avataaars as pa
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional, Dict, Tuple, Union, Any

from sqlmodel import Session, select
from mutagen.id3 import USLT

from . import database as db
from . import db_helpers
from .utils import get_audio_object, AudioType


def parse_val(rsp: dict, attr: str, val: Any) -> None:
    if val is not None and val != "":
        rsp[attr] = val


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


def get_album_artist_id(track: db.Track) -> int:
    if track.album_artist_id:
        return track.album_artist_id
    if len(track.artists) > 0:
        return track.artists[0].id
    return -1


class AlbumService:
    def __init__(self, session: Session):
        self.DBHelper = db_helpers.AlbumDBHelper(session)

    @staticmethod
    def get_open_subsonic_format(
        album: db.Album, with_songs: bool = False
    ) -> dict[str, Optional[Union[str, int, List[dict]]]]:
        genres: List[List[db.Genre]] = [g.genres for g in album.tracks]
        res_album: dict[str, Optional[Union[str, int, List[dict]]]] = {
            "id": album.id,
            "parent": album.artists[0].id if album.artists[0] is not None else -1,
            "album": album.name,
            "title": album.name,
            "name": album.name,
            "isDir": True,
            "coverArt": f"al-{album.id}",
            "songCount": album.total_tracks,
            "duration": sum([int(t.duration) for t in album.tracks]),
            "playCount": min([t.plays_count for t in album.tracks]),
            "artistId": album.artists[0].id if album.artists[0] is not None else -1,
            "artist": ArtistService.join_artists_names(album.artists),
            "genre": genres[0][0].name if len(genres[0]) > 0 else "Unknown Genre",
        }
        parse_val(res_album, "year", album.year)
        parse_val(res_album, "created", "2999-31-12T11:06:57.000Z")

        if len(album.album_favourites) > 0:
            res_album["starred"] = min(a.added_at for a in album.album_favourites)
        if with_songs:
            tracks = []
            for album_track in album.tracks:
                tracks.append(TrackService.get_open_subsonic_format(album_track))
            res_album["song"] = tracks
        return res_album

    def get_album_by_id(self, id):
        album = self.DBHelper.get_album_by_id(id)
        if album:
            album = self.__class__.get_open_subsonic_format(album, with_songs=True)
        return album

    def get_album_info2(self, id):
        pass

    def get_album_list(
        self,
        type: RequestType,
        size: int = 10,
        offset: int = 0,
        from_year: Optional[str] = None,
        to_year: Optional[str] = None,
        genre: Optional[str] = None,
        music_folder_id: Optional[str] = None,
    ) -> Optional[dict[str, Optional[Union[str, int, List[dict]]]]]:
        result = []
        match type:
            case RequestType.RANDOM:
                albums = self.DBHelper.get_all_albums()
                result = random.sample(albums, min(size, len(albums)))
            case RequestType.BY_NAME:
                result = list(self.DBHelper.get_albums_by_name(size, offset))
            case RequestType.BY_ARTIST:
                albums = list(self.DBHelper.get_all_albums())
                albums.sort(key=lambda album: self.compare_albums_by_artist(album.id))
                result = albums[offset : offset + size]
            case RequestType.BY_YEAR if from_year is not None and to_year is not None:
                albums = self.DBHelper.get_all_albums()
                result = [
                    album
                    for album in albums
                    if album.year
                    and min(from_year, to_year) <= album.year <= max(from_year, to_year)
                ][offset : size + offset]
                if from_year > to_year:
                    result.reverse()
            case (
                RequestType.NEWEST
                | RequestType.HIGHEST
                | RequestType.FREQUENT
                | RequestType.RECENT
                | RequestType.BY_GENRE
            ):
                raise NotImplementedError()
            case _:  # validation error
                return None

        return {"album": [AlbumService.get_open_subsonic_format(a) for a in result]}

    def compare_albums_by_artist(self, album_id: int) -> str:
        artist: Optional[db.Artist] = self.DBHelper.get_album_artist(album_id)
        return "" if artist is None else artist.name

    def get_sorted_artist_albums(self, artistId: int, size: int = 10, offset: int = 0):
        albums = self.DBHelper.get_sorted_artist_albums(artistId, size, offset)
        return {"album": [AlbumService.get_open_subsonic_format(a) for a in albums]}


class TrackService:
    def __init__(self, session: Session):
        self.DBHelper = db_helpers.TrackDBHelper(session)
        self.genre_helper = db_helpers.GenresDBHelper(session)

    @staticmethod
    def get_open_subsonic_format(
        track: db.Track, with_genres=False, with_artists=False
    ):
        res_song = {
            "id": track.id,
            "parent": track.album_id,
            "isDir": False,
            "title": track.title,
            "album": track.album.name,
            "artist": ArtistService.join_artists_names(track.artists),
            "track": 1,
            "coverArt": f"mf-{track.id}",
            "size": track.file_size,
            "contentType": track.type,
            "suffix": "mp3",
            "duration": int(track.duration),
            "bitRate": track.bit_rate,
            "bitDepth": track.bits_per_sample,
            "samplingRate": track.sample_rate,
            "channelCount": track.channels,
            "path": track.file_path,
            "playCount": track.plays_count,
            "discNumber": 1,
            "albumId": track.album_id,
            "artistId": get_album_artist_id(track),
            "type": track.type,
            "isVideo": False,
        }
        parse_val(res_song, "year", track.year)
        parse_val(res_song, "created", "2999-31-12T11:06:57.000Z")
        if len(track.track_favourites) > 0:
            res_song["starred"] = min(t.added_at for t in track.track_favourites)
        if with_genres:
            genres = []
            for genre in track.genres:
                genres.append(
                    GenreService.get_open_subsonic_format(genre, item_genre=True)
                )
            res_song["genres"] = genres
        if with_artists:
            artists = []
            for artist in track.artists:
                artists.append(ArtistService.get_open_subsonic_format(artist))
            res_song["artists"] = artists
        return res_song

    def get_song_by_id(self, id):
        track = self.DBHelper.get_track_by_id(id)
        if track:
            track = self.__class__.get_open_subsonic_format(
                track, with_genres=True, with_artists=True
            )
        return track

    def _get_tracks_by_genre_without_subsonic(
        self, genre, count=10, offset=0, music_folder=None
    ):
        genre = self.genre_helper.get_genres_by_name(filter_name=genre)
        return [] if not genre else genre[-1].tracks[offset : offset + count]

    def get_songs_by_genre(self, genre, count=10, offset=0, music_folder=None):
        return [
            self.get_open_subsonic_format(track, with_genres=False)
            for track in self._get_tracks_by_genre_without_subsonic(
                genre, count, offset, music_folder
            )
        ]

    def get_random_songs(
        self,
        size=10,
        genre: Optional[str] = None,
        from_year: Optional[str] = None,
        to_year: Optional[str] = None,
        music_folder_id: Optional[str] = None,
    ):
        tracks = self.DBHelper.get_all_tracks()
        if genre:
            tracks = self._get_tracks_by_genre_without_subsonic(genre)
        if from_year:
            tracks = list(
                filter(lambda track: track.year and track.year >= from_year, tracks)
            )
        if to_year:
            tracks = list(
                filter(lambda track: track.year and track.year <= to_year, tracks)
            )
        random_tracks = random.sample(tracks, min(size, len(tracks)))
        return [
            self.get_open_subsonic_format(track, with_genres=False, with_artists=False)
            for track in random_tracks
        ]

    def extract_lyrics(self, id: int):
        track = self.DBHelper.get_track_by_id(id)
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
                    return [
                        {"text": tag.splitlines()}
                        for tag in audio.tags.get("lyrics", [])
                    ]
        else:
            return None


class GenreService:
    def __init__(self, session: Session):
        self.DBHelper = db_helpers.GenresDBHelper(session)

    @staticmethod
    def get_open_subsonic_format(genre: db.Genre, item_genre=False):
        if item_genre:
            return {"name": genre.name}
        res_genre = {
            "songCount": len(genre.tracks),
            "AlbumCount": len(set([a.album.name for a in genre.tracks])),
            "value": genre.name,
        }

        return res_genre

    def get_genres(self):
        genres = self.DBHelper.get_all_genres()
        if genres:
            genres = {
                "genre:": [self.__class__.get_open_subsonic_format(g) for g in genres]
            }
        return genres


class ArtistService:
    def __init__(self, session: Session):
        self.DBHelper = db_helpers.ArtistDBHelper(session)

    @staticmethod
    def join_artists_names(artists: List[db.Artist]):
        return ", ".join(a.name for a in artists)

    @staticmethod
    def get_open_subsonic_format(
        artist: db.Artist, with_albums: bool = False, with_tracks: bool = False
    ) -> dict[str, Optional[Union[str, int, List[dict]]]]:
        res_artist: dict[str, Optional[Union[str, int, List[dict]]]] = {
            "id": artist.id,
            "name": artist.name,
            "coverArt": f"ar-{artist.id}",
            "albumCount": len(artist.albums),
        }
        if len(artist.artist_favourites) > 0:
            min(a.added_at for a in artist.artist_favourites)
        if with_albums:
            albums = []
            for i in artist.albums:
                albums.append(AlbumService.get_open_subsonic_format(i))
            res_artist["album"] = albums
        if with_tracks:
            tracks = []
            for i in artist.tracks:
                tracks.append(TrackService.get_open_subsonic_format(i))
            res_artist["song"] = tracks
        return res_artist

    def get_artist_by_id(self, id):
        artist = self.DBHelper.get_artist_by_id(id)
        if artist:
            artist = self.__class__.get_open_subsonic_format(
                artist, with_albums=True, with_tracks=True
            )
        return artist

    def get_artists(self, music_folder=None):
        pass

    def get_artist_info2(self, id, count=20, include_not_present=False):
        pass


class SearchService:
    def __init__(self, session: Session):
        self.ArtistDBHelper = db_helpers.ArtistDBHelper(session)
        self.AlbumDBHelper = db_helpers.AlbumDBHelper(session)
        self.TrackDBHelper = db_helpers.TrackDBHelper(session)

    @staticmethod
    def get_open_subsonic_format(
        artists: List[db.Artist], albums: List[db.Album], tracks: List[db.Track]
    ):

        res_search = {
            "artist": [ArtistService.get_open_subsonic_format(a) for a in artists],
            "album": [AlbumService.get_open_subsonic_format(a) for a in albums],
            "song": [TrackService.get_open_subsonic_format(a) for a in tracks],
        }

        return res_search

    def search2(
        self,
        query,
        artist_count,
        artist_offset,
        album_count,
        album_offset,
        song_count,
        song_offset,
    ):
        artists = self.ArtistDBHelper.get_all_artists(filter_name=query)
        if artist_count * artist_offset >= len(artists):
            artists = []
        else:
            artists = artists[
                artist_count
                * artist_offset : min(
                    len(artists), artist_count * artist_offset + artist_count
                )
            ]

        albums = self.AlbumDBHelper.get_all_albums(filter_name=query)
        if album_count * album_offset >= len(albums):
            albums = []
        else:
            albums = albums[
                album_count
                * album_offset : min(
                    len(albums), album_count * album_offset + album_count
                )
            ]

        tracks = self.TrackDBHelper.get_all_tracks(filter_title=query)
        if song_count * song_offset >= len(tracks):
            tracks = []
        else:
            tracks = tracks[
                song_count
                * song_offset : min(len(tracks), song_count * song_offset + song_count)
            ]

        return self.__class__.get_open_subsonic_format(artists, albums, tracks)

    def search3(
        self,
        query,
        artist_count,
        artist_offset,
        album_count,
        album_offset,
        song_count,
        song_offset,
    ):
        if query != "":
            return self.search2(
                query,
                artist_count,
                artist_offset,
                album_count,
                album_offset,
                song_count,
                song_offset,
            )
        artists = self.ArtistDBHelper.get_all_artists()
        albums = self.AlbumDBHelper.get_all_albums()
        tracks = self.TrackDBHelper.get_all_tracks()
        return self.__class__.get_open_subsonic_format(artists, albums, tracks)


class StarService:
    def __init__(self, session: Session):
        self.DBHelper = db_helpers.FavouriteDBHelper(session)

    def star(self, track_id, album_id, artist_id, playlist_id, user_id=0):
        for id in track_id:
            self.DBHelper.star_track(id, user_id)
        for id in artist_id:
            self.DBHelper.star_artist(id, user_id)
        for id in album_id:
            self.DBHelper.star_album(id, user_id)
        for id in playlist_id:
            self.DBHelper.star_playlist(id, user_id)

    def unstar(self, track_id, album_id, artist_id, playlist_id, user_id=0):
        for id in track_id:
            self.DBHelper.unstar_track(id, user_id)
        for id in artist_id:
            self.DBHelper.unstar_artist(id, user_id)
        for id in album_id:
            self.DBHelper.unstar_album(id, user_id)
        for id in playlist_id:
            self.DBHelper.unstar_playlist(id, user_id)

    def get_starred(self, user_id=0):
        tracks = self.DBHelper.get_starred_tracks(user_id)
        albums = self.DBHelper.get_starred_albums(user_id)
        artists = self.DBHelper.get_starred_artists(user_id)
        playlists = self.DBHelper.get_starred_playlists(user_id)

        tracks = [TrackService.get_open_subsonic_format(t) for t in tracks]
        albums = [AlbumService.get_open_subsonic_format(t) for t in albums]
        artists = [ArtistService.get_open_subsonic_format(t) for t in artists]
        playlists = [PlaylistService.get_open_subsonic_format(t) for t in playlists]
        return {
            "artist": artists,
            "album": albums,
            "song": tracks,
            "playlist": playlists,
        }


class PlaylistService:
    def __init__(self, session: Session):
        self.DBHelper = db_helpers.PlaylistDBHelper(session)

    @staticmethod
    def get_open_subsonic_format(playlist: db.Playlist, with_tracks=False):
        playlist_tracks = playlist.playlist_tracks
        res_playlist: dict[str, Optional[Union[str, int, List[dict]]]] = {
            "id": playlist.id,
            "name": playlist.name,
            "owner": playlist.user.login,
            "public": True,
            "created": playlist.create_date,
            "changed": max(
                [a.added_at for a in playlist_tracks], default=playlist.create_date
            ),
            "songCount": playlist.total_tracks,
            "duration": sum(t.track.duration for t in playlist_tracks),
        }
        if with_tracks:
            tracks = [
                TrackService.get_open_subsonic_format(t.track) for t in playlist_tracks
            ]
            res_playlist["entry"] = tracks
        return res_playlist

    def create_playlist(self, name, tracks, user_id):
        playlist_id = self.DBHelper.create_playlist(name, tracks, user_id)
        return self.get_playlist(playlist_id)

    def update_playlist(self, id, name, tracks_to_add, tracks_to_remove):
        playlist = self.DBHelper.update_playlist(
            id, name, tracks_to_add, tracks_to_remove
        )
        if playlist:
            playlist = self.__class__.get_open_subsonic_format(
                playlist, with_tracks=True
            )
        return playlist

    def delete_playlist(self, id):
        self.DBHelper.delete_playlist(id)

    def get_playlist(self, id):
        playlist = self.DBHelper.get_playlist(id)
        if playlist:
            playlist = self.__class__.get_open_subsonic_format(
                playlist, with_tracks=True
            )
        return playlist

    def get_playlists(self, music_folder=None):
        playlists = self.DBHelper.get_all_playlists()
        playlists = [self.get_open_subsonic_format(i) for i in playlists]
        return {"playlist": playlists}


class IndexService:
    def __init__(self, session: Session):
        self.ArtistDBHelper = db_helpers.ArtistDBHelper(session)
        self.TrackDBHelper = db_helpers.TrackDBHelper(session)

    @dataclass
    class ArtistIndex:
        name: str
        artist: List[db.Artist]

        def get_open_subsonic_format(self):
            return {
                "name": self.name,
                "artist": [
                    ArtistService.get_open_subsonic_format(a) for a in self.artist
                ],
            }

    def get_indexes_artists(
        self,
        music_folder_id: str = "",
        if_modified_since_ms: int = 0,
        with_childs: bool = False,
    ) -> Dict[str, List[Dict]]:
        artists: List[db.Artist] = list(self.ArtistDBHelper.get_all_artists())
        artists.sort(key=lambda a: a.name)
        index: List[IndexService.ArtistIndex] = []
        letter: str = ""
        letter_artists: List[db.Artist] = []
        for a in artists:
            if len(a.name) > 0 and a.name[0] != letter:
                if len(letter_artists) > 0:
                    index.append(IndexService.ArtistIndex(letter, letter_artists))
                letter = a.name[0]
                letter_artists = []
            letter_artists.append(a)
        res = {
            "index": [indexArtist.get_open_subsonic_format() for indexArtist in index]
        }
        if with_childs:
            tracks: List[str] = []
            for a in artists:
                ts: List[db.Track] = self.TrackDBHelper.get_track_by_artist_id(a.id)
                for t in ts:
                    tracks.append(TrackService.get_open_subsonic_format(t))
            res["child"] = tracks
        return res


def random_enum_choice(e):
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
    return avatar.render_png()


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
