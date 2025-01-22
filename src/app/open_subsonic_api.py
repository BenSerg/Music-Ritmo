from typing import Optional, List

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from . import database as db

open_subsonic_router = APIRouter(prefix="/rest")


class SubsonicResponse:
    def __init__(self):
        self.data = {}
        self.data["status"] = "ok"
        self.data["version"] = "1.16.1"
        self.data["type"] = "MusicRitmo"
        self.data["serverVersion"] = "0.1"
        self.data["openSubsonic"] = True

    def to_json_rsp(self) -> JSONResponse:
        return JSONResponse({"subsonic-response": self.data})


class SubsonicTrack(BaseModel):
    id: str = Field(default_factory=str)
    parent: str = Field(default_factory=str)
    title: str = Field(default_factory=str)
    isDir: bool = False
    isVideo: bool = False
    type: str = "music"
    albumId: str = Field(default_factory=str)
    album: str = ""
    artistId: str = Field(default_factory=str)
    artist: str = ""
    coverArt: Optional[str] = None
    duration: float = 0
    bitRate: int = 0
    bitDepth: int = 16
    samplingRate: int = 44100
    channelCount: int = 2
    userRating: int = 0
    averageRating: float = 0.0
    track: int = 1
    year: str = ""
    genre: str = ""
    size: int = 0
    discNumber: int = 1
    suffix: str = Field(default_factory=str)
    contentType: str = "audio/mpeg"
    path: str = Field(default_factory=str)


@open_subsonic_router.get("/ping")
async def ping():
    rsp = SubsonicResponse()
    return rsp.to_json_rsp()


@open_subsonic_router.get("/getPlaylists")
async def get_playlists(session: Session = Depends(db.get_session)):
    rsp = SubsonicResponse()

    playlists = session.exec(select(db.Playlist)).all()

    playlist_data = [
        {
            "id": playlist.id,
            "name": playlist.name,
            "owner": playlist.user_id,
            "songCount": playlist.total_tracks,
            "createDate": playlist.create_date,
        }
        for playlist in playlists
    ]

    rsp.data["playlists"] = {"playlist": playlist_data}

    return rsp.to_json_rsp()


@open_subsonic_router.get("/scroble")
def scroble(id: int, session: Session = Depends(db.get_session)):
    track = session.exec(select(db.Track).where(db.Track.id == id)).first()
    if track is None:
        return JSONResponse({"detail": "No such id"}, status_code=404)

    track.plays_count += 1
    session.add(track)
    session.commit()

    rsp = SubsonicResponse()
    return rsp.to_json_rsp()


@open_subsonic_router.get("/getSongsByGenre")
def get_songs_by_genre(genre: str, session: Session = Depends(db.get_session)):
    rsp = SubsonicResponse()
    genre_record = session.exec(
        select(db.Genre).where(db.Genre.name == genre)
    ).one_or_none()

    tracks_data = []
    for track in genre_record.tracks:
        track_info = SubsonicTrack()
        track_info.id = str(track.id)
        track_info.title = track.title
        track_info.albumId = str(track.album_id)
        track_info.album = track.album.name
        track_info.artistId = str(track.artists[0].id)
        artist = [a.name for a in track.artists]
        track_info.artist = ", ".join(artist)
        track_info.genre = track.genres[0].name
        track_info.duration = track.duration
        track_info.year = track.year
        track_info.path = track.file_path
        tracks_data.append(track_info.model_dump())

    rsp.data["songsByGenre"] = {"song": tracks_data}
    return rsp.to_json_rsp()


@open_subsonic_router.get("/download")
async def download(id: int, session: Session = Depends(db.get_session)):
    track = session.exec(select(db.Track).where(db.Track.id == id)).first()
    if track is None:
        return JSONResponse({"detail": "No such id"}, status_code=404)

    return FileResponse(track.file_path)


@open_subsonic_router.get("/stream")
async def download(id: int, session: Session = Depends(db.get_session)):
    track = session.exec(select(db.Track).where(db.Track.id == id)).first()
    if track is None:
        return JSONResponse({"detail": "No such id"}, status_code=404)

    return FileResponse(track.file_path)


@open_subsonic_router.get("/search2")
async def search2(
    query: str = Query(),
    artistCount: int = Query(default=20),
    artistOffset: int = Query(default=0),
    albumCount: int = Query(default=20),
    albumOffset: int = Query(default=0),
    songCount: int = Query(default=20),
    songOffset: int = Query(default=0),
    session: Session = Depends(db.get_session),
):
    name = query
    artists = session.exec(select(db.Artist)).all()
    if artistCount * artistOffset >= len(artists):
        artists = []
    else:
        artists = [a for a in artists if name in a.name]
        albumNum = [len(a.albums) for a in artists]
        artists = [a.model_dump() for a in artists]
        for i in range(len(artists)):
            artists[i]["albumCount"] = albumNum[i]
            artists[i]["coverArt"] = "ar-100000002"
            artists[i]["starred"] = "2021-02-22T05:54:18Z"
        artists = artists[
            artistCount
            * artistOffset : min(len(artists), artistCount * artistOffset + artistCount)
        ]

    albums = session.exec(select(db.Album)).all()
    if albumCount * albumOffset >= len(albums):
        albums = []
    else:
        albums = [a for a in albums if name in a.name]
        songs = [s.tracks for s in albums]
        names = [n.name for n in albums]
        years = [y.year for y in albums]
        albArtists = [a.artists for a in albums]
        albums = [a.model_dump() for a in albums]
        for i in range(len(albums)):
            albums[i]["parent"] = (
                albArtists[i][0].id if albArtists[i][0] is not None else -1
            )
            albums[i]["coverArt"] = "ar-100000002"
            albums[i]["album"] = names[i]
            albums[i]["title"] = names[i]
            albums[i]["name"] = names[i]
            albums[i]["created"] = years[i]
            albums[i]["year"] = years[i]
            albums[i]["isDir"] = True
            albums[i]["songCount"] = len(songs[i])
            albums[i]["playCount"] = 0
            albums[i]["artistId"] = (
                albArtists[i][0].id if albArtists[i][0] is not None else -1
            )
            albums[i]["artist"] = albArtists[i][0].name
            duration = sum([s.duration for s in songs[i]])
            albums[i]["duration"] = duration
            genres = [g.genres for g in songs[i]]
            albums[i]["genre"] = "Pop"
        albums = albums[
            albumCount
            * albumOffset : min(len(albums), albumCount * albumOffset + albumCount)
        ]

    tracks = session.exec(select(db.Track)).all()
    if songCount * songOffset >= len(tracks):
        tracks = []
    else:
        tracks = [a for a in tracks if name in a.title]
        artistTrack = [a.artists for a in tracks]
        albumTrack = [a.album for a in tracks]
        trackTitles = [t.title for t in tracks]
        filePath = [p.file_path for p in tracks]
        playCount = [c.plays_count for c in tracks]
        years = [y.year for y in tracks]
        types = [t.type for t in tracks]
        tracks = [t.model_dump() for t in tracks]
        for i in range(len(tracks)):
            tracks[i]["parent"] = albumTrack[i].id if albumTrack[i] is not None else -1
            tracks[i]["isDir"] = False
            tracks[i]["title"] = trackTitles[i]
            tracks[i]["album"] = (
                albumTrack[i].name if albumTrack[i] is not None else "Unknown Album"
            )
            artist = [a.name for a in artistTrack[i]]
            tracks[i]["artist"] = " ".join(artist)
            tracks[i]["track"] = 1
            tracks[i]["coverArt"] = ["mf-082f435a363c32c57d5edb6a678a28d4_6410b3ce"]
            tracks[i]["size"] = 19866778
            tracks[i]["contentType"] = types[i]
            tracks[i]["suffix"] = "mp3"
            tracks[i]["starred"] = "2023-03-27T09:45:27Z"
            tracks[i]["bitRate"] = 880
            tracks[i]["bitDepth"] = 16
            tracks[i]["simplingRate"] = 44100
            tracks[i]["channelCount"] = 2
            tracks[i]["path"] = filePath[i]
            tracks[i]["playCount"] = playCount[i]
            tracks[i]["discNumber"] = 1
            tracks[i]["created"] = years[i]
            tracks[i]["albumId"] = albumTrack[i].id if albumTrack[i] is not None else -1
            tracks[i]["artistId"] = (
                artistTrack[i][0].id if len(artistTrack[i]) > 0 else -1
            )
            tracks[i]["type"] = types[i]
            tracks[i]["isVideo"] = False
        tracks = tracks[
            songCount
            * songOffset : min(len(tracks), songCount * songOffset + songCount)
        ]

    searchResult = {}
    searchResult["artist"] = artists
    searchResult["song"] = tracks
    searchResult["album"] = albums
    rsp = SubsonicResponse()
    rsp.data["searchResult"] = searchResult

    return rsp.to_json_rsp()


@open_subsonic_router.get("/getGenres")
async def getGenres(session: Session = Depends(db.get_session)):
    genres = session.exec(select(db.Genre)).all()
    genresValue = [v.name for v in genres]
    tracks = [g.tracks for g in genres]
    genres = [{} for g in genres]
    for i in range(len(genres)):
        genres[i]["value"] = genresValue[i]
        genres[i]["songCount"] = len(tracks[i])
        albums = [a.album.name for a in tracks[i]]
        albums = set(albums)
        genres[i]["albumCount"] = len(albums)
    genresResult = {}
    genresResult["genre"] = genres
    rsp = SubsonicResponse()
    rsp.data["genres"] = genresResult

    return rsp.to_json_rsp()


@open_subsonic_router.get("/getSong")
def getSong(id: int, session: Session = Depends(db.get_session)):
    track = session.exec(select(db.Track).where(db.Track.id == id)).first()
    if track is None:
        return JSONResponse({"detail": "No such id"}, status_code=404)
    
    track_info = SubsonicTrack()
    track_info.id = str(track.id)
    track_info.title = track.title
    track_info.albumId = str(track.album_id)
    track_info.album = track.album.name
    track_info.artistId = str(track.artists[0].id)
    artist = [a.name for a in track.artists]
    track_info.artist = ", ".join(artist)
    track_info.genre = track.genres[0].name
    track_info.duration = track.duration
    track_info.year = track.year
    track_info.path = track.file_path

    rsp = SubsonicResponse()
    rsp.data["song"] = track_info.model_dump()
    return rsp.to_json_rsp()

@open_subsonic_router.get("/getArtist")
async def getArtist(id: int = Query(), session: Session = Depends(db.get_session)):
    artist = session.exec(select(db.Artist).where(db.Artist.id == id)).one_or_none()
    if artist is None:
        return JSONResponse(content={"message": "Not Found"}, status_code=404)
    albums = artist.albums
    songs = [s.tracks for s in albums]
    names = [n.name for n in albums]
    years = [y.year for y in albums]
    albArtists = [a.artists for a in albums]
    albums = [{"id": a.id} for a in albums]
    for i in range(len(albums)):
        albums[i]["parent"] = (
            albArtists[i][0].id if albArtists[i][0] is not None else -1
        )
        albums[i]["coverArt"] = "ar-100000002"
        albums[i]["album"] = names[i]
        albums[i]["title"] = names[i]
        albums[i]["name"] = names[i]
        albums[i]["created"] = years[i]
        albums[i]["year"] = years[i]
        albums[i]["isDir"] = True
        albums[i]["songCount"] = len(songs[i])
        playCount = [p.plays_count for p in songs[i]]
        albums[i]["playCount"] = min(playCount)
        albums[i]["artistId"] = (
            albArtists[i][0].id if albArtists[i][0] is not None else -1
        )
        albums[i]["artist"] = albArtists[i][0].name
        duration = sum([s.duration for s in songs[i]])
        albums[i]["duration"] = duration
        genres = [g.genres for g in songs[i]]
        albums[i]["genre"] = (
            genres[0][0].name if len(genres[0]) > 0 else "Unknown Genre"
        )
    resArtist = {}
    resArtist["id"] = artist.id
    resArtist["name"] = artist.name
    resArtist["album"] = albums
    resArtist["coverArt"] = f"ar-{id}"
    resArtist["albumCount"] = len(albums)
    resArtist["starred"] = ""
    rsp = SubsonicResponse()
    rsp.data["artist"] = resArtist

    return rsp.to_json_rsp()
