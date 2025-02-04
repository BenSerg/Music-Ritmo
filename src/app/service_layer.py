import random
from dataclasses import dataclass
from typing import List, Optional, Dict, Union

from sqlmodel import Session

from . import database as db
from . import db_helpers


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
            "created": album.year,
            "duration": sum([int(t.duration) for t in album.tracks]),
            "playCount": min([t.plays_count for t in album.tracks]),
            "artistId": album.artists[0].id if album.artists[0] is not None else -1,
            "artist": (
                album.artists[0].name
                if album.artists[0] is not None
                else "Unknown Artist"
            ),
            "year": album.year,
            "starred": "",
            "genre": genres[0][0].name if len(genres[0]) > 0 else "Unknown Genre",
        }
        if with_songs:
            tracks = []
            for album_track in album.tracks:
                tracks.append(TrackService.get_open_subsonic_format(album_track))
            res_album["song"] = tracks  # Здесь tracks - это список
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
        type,
        size=10,
        offset=10,
        from_year=None,
        to_year=None,
        genre=None,
        music_folder_id=None,
    ):
        pass


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
            "year": track.year,
            "coverArt": f"mf-{track.id}",
            "size": track.file_size,
            "contentType": track.type,
            "suffix": "mp3",
            "starred": "",
            "duration": track.duration,
            "bitRate": track.bit_rate,
            "bitDepth": track.bits_per_sample,
            "samplingRate": track.sample_rate,
            "channelCount": track.channels,
            "path": track.file_path,
            "playCount": track.plays_count,
            "discNumber": 1,
            "created": track.year,
            "albumId": track.album_id,
            "artistId": track.artists[0].id if len(track.artists) > 0 else -1,
            "type": track.type,
            "isVideo": False,
        }
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
        artist: db.Artist, with_albums: bool = False
    ) -> dict[str, Optional[Union[str, int, List[dict]]]]:
        res_artist: dict[str, Optional[Union[str, int, List[dict]]]] = {
            "id": artist.id,
            "name": artist.name,
            "coverArt": f"ar-{artist.id}",
            "albumCount": len(artist.albums),
            "starred": None,
        }
        if with_albums:
            albums = []
            for i in artist.albums:
                albums.append(AlbumService.get_open_subsonic_format(i))
            res_artist["album"] = albums
        return res_artist

    def get_artist_by_id(self, id):
        artist = self.DBHelper.get_artist_by_id(id)
        if artist:
            artist = self.__class__.get_open_subsonic_format(artist, with_albums=True)
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
                ts: List[db.Track] = self.TrackDBHelper.get_track_by_id(a.id)
                for t in ts:
                    tracks.append(TrackService.get_open_subsonic_format(t))
            res["child"] = tracks
        return res
