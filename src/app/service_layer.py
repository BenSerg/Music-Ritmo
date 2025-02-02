import random
from typing import List, Optional
from sqlmodel import Session
from . import db_helpers
from . import database as db


class AlbumService:
    def __init__(self, session: Session):
        self.DBHelper = db_helpers.AlbumDBHelper(session)

    @staticmethod
    def getOpenSubsonicFormat(album: db.Album, withSongs=False):
        genres = [g.genres for g in album.tracks]
        resAlbum = {
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
        if withSongs:
            tracks = []
            for i in album.tracks:
                tracks.append(TrackService.getOpenSubsonicFormat(i))
            resAlbum["song"] = tracks
        return resAlbum

    def getAlbumById(self, id):
        album = self.DBHelper.getAlbumById(id)
        if album:
            album = self.__class__.getOpenSubsonicFormat(album, withSongs=True)
        return album

    def getAlbumInfo2(self, id):
        pass

    def getAlbumList(
            self,
            type,
            size=10,
            offset=10,
            fromYear=None,
            toYear=None,
            genre=None,
            musicFolderId=None,
    ):
        pass


class TrackService:
    def __init__(self, session: Session):
        self.DBHelper = db_helpers.TrackDBHelper(session)
        self.genre_helper = db_helpers.GenresDBHelper(session)

    @staticmethod
    def getOpenSubsonicFormat(track: db.Track, withGenres=False, withArtists=False):
        resSong = {
            "id": track.id,
            "parent": track.album_id,
            "isDir": False,
            "title": track.title,
            "album": track.album.name,
            "artist": ArtistService.joinArtistsNames(track.artists),
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
        if withGenres:
            genres = []
            for i in track.genres:
                genres.append(GenreService.getOpenSubsonicFormat(i, ItemGenre=True))
            resSong["genres"] = genres
        if withArtists:
            artists = []
            for i in track.artists:
                artists.append(ArtistService.getOpenSubsonicFormat(i))
            resSong["artists"] = artists
        return resSong

    def getSongById(self, id):
        track = self.DBHelper.getTrackById(id)
        if track:
            track = self.__class__.getOpenSubsonicFormat(track, withGenres=True, withArtists=True)
        return track

    def _get_tracks_by_genre_without_subsonic(self, genre, count=10, offset=0, musicFolder=None):
        genre = self.genre_helper.getAllGenres(filterName=genre)
        return genre[-1].tracks[offset:offset + count]

    def getSongsByGenre(self, genre, count=10, offset=0, musicFolder=None):
        return [self.getOpenSubsonicFormat(track, withGenres=False) for track in
                self._get_tracks_by_genre_without_subsonic(genre, count, offset, musicFolder)]

    def getRandomSongs(
            self, size=10,
            genre: Optional[str] = None,
            fromYear: Optional[str] = None,
            toYear: Optional[str] = None,
            musicFolderId: Optional[str] = None
    ):
        tracks = self.DBHelper.getAllTracks()
        if genre:
            tracks = self._get_tracks_by_genre_without_subsonic(genre)
        if fromYear:
            tracks = list(filter(lambda track: track.year and int(track.year) >= int(fromYear), tracks))
        if toYear:
            tracks = list(filter(lambda track: track.year and int(track.year) <= int(toYear), tracks))
        random_tracks = random.sample(tracks, min(size, len(tracks)))
        return [self.getOpenSubsonicFormat(track, withGenres=False, withArtists=False) for track in random_tracks]


class GenreService:
    def __init__(self, session: Session):
        self.DBHelper = db_helpers.GenresDBHelper(session)

    @staticmethod
    def getOpenSubsonicFormat(genre: db.Genre, ItemGenre=False):
        if ItemGenre:
            return {"name": genre.name}
        resGenre = {
            "songCount": len(genre.tracks),
            "AlbumCount": len(set([a.album.name for a in genre.tracks])),
            "value": genre.name,
        }

        return resGenre

    def getGenres(self):
        genres = self.DBHelper.getAllGenres()
        if genres:
            genres = {"genre:": [self.__class__.getOpenSubsonicFormat(g) for g in genres]}
        return genres


class ArtistService:
    def __init__(self, session: Session):
        self.DBHelper = db_helpers.ArtistDBHelper(session)

    @staticmethod
    def joinArtistsNames(artists: List[db.Artist]):
        return ", ".join(a.name for a in artists)

    @staticmethod
    def getOpenSubsonicFormat(artist: db.Artist, withAlbums=False):
        resArtist = {
            "id": artist.id,
            "name": artist.name,
            "coverArt": f"ar-{artist.id}",
            "albumCount": len(artist.albums),
            "starred": "",
        }
        if withAlbums:
            albums = []
            for i in artist.albums:
                albums.append(AlbumService.getOpenSubsonicFormat(i))
            resArtist["album"] = albums
        return resArtist

    def getArtistById(self, id):
        artist = self.DBHelper.getArtistById(id)
        if artist:
            artist = self.__class__.getOpenSubsonicFormat(artist, withAlbums=True)
        return artist

    def getArtists(self, musicFolder=None):
        pass

    def getArtistInfo2(self, id, count=20, includeNotPresent=False):
        pass


class SearchService:
    def __init__(self, session: Session):
        self.ArtistDBHelper = db_helpers.ArtistDBHelper(session)
        self.AlbumDBHelper = db_helpers.AlbumDBHelper(session)
        self.TrackDBHelper = db_helpers.TrackDBHelper(session)

    @staticmethod
    def getOpenSubsonicFormat(
            artists: List[db.Artist], albums: List[db.Album], tracks: List[db.Track]
    ):

        resSearch = {
            "artist": [ArtistService.getOpenSubsonicFormat(a) for a in artists],
            "album": [AlbumService.getOpenSubsonicFormat(a) for a in albums],
            "song": [TrackService.getOpenSubsonicFormat(a) for a in tracks],
        }

        return resSearch

    def search2(
            self,
            query,
            artistCount,
            artistOffset,
            albumCount,
            albumOffset,
            songCount,
            songOffset,
    ):
        artists = self.ArtistDBHelper.getAllArtists(filterName=query)
        if artistCount * artistOffset >= len(artists):
            artists = []
        else:
            artists = artists[
                      artistCount
                      * artistOffset: min(
                          len(artists), artistCount * artistOffset + artistCount
                      )
                      ]

        albums = self.AlbumDBHelper.getAllAlbums(filterName=query)
        if albumCount * albumOffset >= len(albums):
            albums = []
        else:
            albums = albums[
                     albumCount
                     * albumOffset: min(len(albums), albumCount * albumOffset + albumCount)
                     ]

        tracks = self.TrackDBHelper.getAllTracks(filterTitle=query)
        if songCount * songOffset >= len(tracks):
            tracks = []
        else:
            tracks = tracks[
                     songCount
                     * songOffset: min(len(tracks), songCount * songOffset + songCount)
                     ]

        return self.__class__.getOpenSubsonicFormat(artists, albums, tracks)
