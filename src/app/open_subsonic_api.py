from typing import Optional, List

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from . import database as db
from . import service_layer

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
    service = service_layer.SearchService(session)
    result = service.search2(
        query, artistCount, artistOffset, albumCount, albumOffset, songCount, songOffset
    )
    rsp = SubsonicResponse()
    rsp.data["searchResult2"] = result

    return rsp.to_json_rsp()


@open_subsonic_router.get("/search3")
async def search3(
    query: str = Query(),
    artistCount: int = Query(default=20),
    artistOffset: int = Query(default=0),
    albumCount: int = Query(default=20),
    albumOffset: int = Query(default=0),
    songCount: int = Query(default=20),
    songOffset: int = Query(default=0),
    session: Session = Depends(db.get_session),
):
    service = service_layer.SearchService(session)
    result = service.search3(
        query, artistCount, artistOffset, albumCount, albumOffset, songCount, songOffset
    )
    rsp = SubsonicResponse()
    rsp.data["searchResult3"] = result

    return rsp.to_json_rsp()


@open_subsonic_router.get("/getGenres")
async def getGenres(session: Session = Depends(db.get_session)):
    serice = service_layer.GenreService(session)
    genresResult = serice.getGenres()
    rsp = SubsonicResponse()
    rsp.data["genres"] = genresResult

    return rsp.to_json_rsp()


@open_subsonic_router.get("/getSong")
def getSong(id: int, session: Session = Depends(db.get_session)):
    service = service_layer.TrackService(session)
    track = service.getSongById(id)
    if track is None:
        return JSONResponse({"detail": "No such id"}, status_code=404)

    rsp = SubsonicResponse()
    rsp.data["song"] = track
    return rsp.to_json_rsp()


@open_subsonic_router.get("/getArtist")
def getArtist(id: int, session: Session = Depends(db.get_session)):
    service = service_layer.ArtistService(session)
    artist = service.getArtistById(id)
    if artist is None:
        return JSONResponse({"detail": "No such id"}, status_code=404)

    rsp = SubsonicResponse()
    rsp.data["artist"] = artist
    return rsp.to_json_rsp()


@open_subsonic_router.get("/getAlbum")
def getAlbum(id: int, session: Session = Depends(db.get_session)):
    service = service_layer.AlbumService(session)
    album = service.getAlbumById(id)
    if album is None:
        return JSONResponse({"detail": "No such id"}, status_code=404)

    rsp = SubsonicResponse()
    rsp.data["album"] = album
    return rsp.to_json_rsp()


@open_subsonic_router.get("/getIndexes")
def getIndexes(
    musicFolderId: str = Query(default=""),
    ifModifiedSince: int = Query(default=0),
    session: Session = Depends(db.get_session),
):
    indexService = service_layer.IndexService(session)

    indexes = indexService.getIndexesArtists(
        musicFolderId, ifModifiedSince, withChilds=True
    )

    rsp = SubsonicResponse()
    rsp.data["indexes"] = indexes
    rsp.data["indexes"]["ignoredArticles"] = ""
    rsp.data["indexes"]["lastModified"] = 0
    return rsp.to_json_rsp()


@open_subsonic_router.get("/getArtists")
def getArtists(
    musicFolderId: str = Query(default=""),
    session: Session = Depends(db.get_session),
):
    indexService = service_layer.IndexService(session)

    indexes = indexService.getIndexesArtists(musicFolderId)

    rsp = SubsonicResponse()
    rsp.data["artists"] = indexes
    rsp.data["artists"]["ignoredArticles"] = ""
    return rsp.to_json_rsp()
