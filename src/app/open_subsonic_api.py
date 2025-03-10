from typing import Optional, List
import asyncio

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse, FileResponse, Response
from pydantic import BaseModel, Field
from sqlmodel import Session, select
from PIL import Image

from src.app.open_subsonic_formatter import OpenSubsonicFormatter
from .subsonic_response import SubsonicResponse
from .auth import authenticate_user
from src.app import dto

from . import database as db
from . import service_layer
from . import db_helpers
from . import db_loading
from . import utils

open_subsonic_router = APIRouter(prefix="/rest")


@open_subsonic_router.get("/createUser")
async def create_user(
    username: str = Query(...),
    password: str = Query(...),
    email: str = Query(default=""),
    session: Session = Depends(db.get_session),
) -> JSONResponse:
    _, err = service_layer.create_user(session, username, password)
    if err:
        return JSONResponse({"detail": err}, status_code=400)

    rsp = SubsonicResponse()
    return rsp.to_json_rsp()


@open_subsonic_router.get("/deleteUser")
async def delete_user(
    username: str = Query(...),
    current_user: db.User = Depends(authenticate_user),
    session: Session = Depends(db.get_session),
) -> JSONResponse:
    user = session.exec(select(db.User).where(db.User.login == username)).one_or_none()
    if user:
        session.delete(user)
        session.commit()
    rsp = SubsonicResponse()
    return rsp.to_json_rsp()


@open_subsonic_router.get("/updateUser")
async def update_user(
    username: str = Query(...),
    password: str = "",
    newUsername: str = "",
    current_user: db.User = Depends(authenticate_user),
    session: Session = Depends(db.get_session),
) -> JSONResponse:
    user = session.exec(select(db.User).where(db.User.login == username)).one_or_none()
    if not user:
        return JSONResponse({"detail": "User not found"}, status_code=404)
    if newUsername:
        user.login = newUsername
    if password:
        user.password = password
    session.commit()
    rsp = SubsonicResponse()
    return rsp.to_json_rsp()


@open_subsonic_router.get("/changePassword")
async def change_password(
    username: str = Query(...),
    password: str = Query(...),
    current_user: db.User = Depends(authenticate_user),
    session: Session = Depends(db.get_session),
) -> JSONResponse:
    user = session.exec(select(db.User).where(db.User.login == username)).one_or_none()
    if not user:
        return JSONResponse({"detail": "User not found"}, status_code=404)
    rsp = SubsonicResponse()
    if user.login != current_user.login:
        rsp.set_error(50, "The user can only change his password")
    else:
        user.password = password
        session.commit()
    return rsp.to_json_rsp()


@open_subsonic_router.get("/getUser")
async def get_user(
    username: str = Query(..., description="Имя пользователя"),
    current_user: db.User = Depends(authenticate_user),
    session: Session = Depends(db.get_session),
) -> JSONResponse:
    user = session.exec(select(db.User).where(db.User.login == username)).one_or_none()
    if not user:
        return JSONResponse({"detail": "User not found"}, status_code=404)
    rsp = SubsonicResponse()
    rsp.data["user"] = {"username": user.login, "folder": [1]}
    return rsp.to_json_rsp()


@open_subsonic_router.get("/getUsers")
async def get_users(
    current_user: db.User = Depends(authenticate_user),
    session: Session = Depends(db.get_session),
) -> JSONResponse:
    users = session.exec(select(db.User)).all()

    rsp = SubsonicResponse()
    rsp.data["users"] = {
        "user": [{"username": user.login, "folder": [1]} for user in users]
    }
    return rsp.to_json_rsp()


@open_subsonic_router.get("/ping")
async def ping() -> JSONResponse:
    rsp = SubsonicResponse()
    return rsp.to_json_rsp()


@open_subsonic_router.get("/getPlaylists")
async def get_playlists(
    username: str = "", session: Session = Depends(db.get_session)
) -> JSONResponse:
    service = service_layer.PlaylistService(session)
    playlists = service.get_playlists()

    rsp = SubsonicResponse()
    rsp.data["playlists"] = OpenSubsonicFormatter.format_playlists(playlists)
    return rsp.to_json_rsp()


@open_subsonic_router.get("/scroble")
def scroble(id: int, session: Session = Depends(db.get_session)) -> JSONResponse:
    track = session.exec(select(db.Track).where(db.Track.id == id)).first()
    if track is None:
        return JSONResponse({"detail": "No such id"}, status_code=404)

    track.plays_count += 1
    session.add(track)
    session.commit()

    rsp = SubsonicResponse()
    return rsp.to_json_rsp()


@open_subsonic_router.get("/getSongsByGenre")
def get_songs_by_genre(
    genre: str, session: Session = Depends(db.get_session)
) -> JSONResponse:
    rsp = SubsonicResponse()
    service = service_layer.TrackService(session)
    tracks = service.get_songs_by_genre(genre)
    rsp.data["songsByGenre"] = OpenSubsonicFormatter.format_tracks(tracks)
    return rsp.to_json_rsp()


@open_subsonic_router.get("/download")
async def download(id: int, session: Session = Depends(db.get_session)) -> Response:
    track = session.exec(select(db.Track).where(db.Track.id == id)).first()
    if track is None:
        return JSONResponse({"detail": "No such id"}, status_code=404)

    return FileResponse(track.file_path)


@open_subsonic_router.get("/stream")
async def stream(id: int, session: Session = Depends(db.get_session)) -> Response:
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
) -> JSONResponse:
    service = service_layer.SearchService(session)
    artists, albums, tracks = service.search2(
        query, artistCount, artistOffset, albumCount, albumOffset, songCount, songOffset
    )
    rsp = SubsonicResponse()
    rsp.data["searchResult2"] = OpenSubsonicFormatter.format_combination(
        artists, albums, tracks
    )

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
) -> JSONResponse:
    service = service_layer.SearchService(session)
    artists, albums, tracks = service.search3(
        query, artistCount, artistOffset, albumCount, albumOffset, songCount, songOffset
    )
    rsp = SubsonicResponse()
    rsp.data["searchResult3"] = OpenSubsonicFormatter.format_combination(
        artists, albums, tracks
    )

    return rsp.to_json_rsp()


@open_subsonic_router.get("/getGenres")
async def get_genres(session: Session = Depends(db.get_session)) -> JSONResponse:
    service = service_layer.GenreService(session)
    genres: List[dto.Genre] = service.get_genres()

    rsp = SubsonicResponse()
    rsp.data["genres"] = OpenSubsonicFormatter.format_genres(genres)

    return rsp.to_json_rsp()


@open_subsonic_router.get("/getSong")
def get_song(id: int, session: Session = Depends(db.get_session)) -> JSONResponse:
    service = service_layer.TrackService(session)
    track: Optional[dto.Track] = service.get_song_by_id(id)
    if track is None:
        return JSONResponse({"detail": "No such id"}, status_code=404)

    rsp = SubsonicResponse()
    rsp.data["song"] = OpenSubsonicFormatter.format_track(track)
    return rsp.to_json_rsp()


@open_subsonic_router.get("/getRandomSongs")
def get_random_songs(
    size: int = 10,
    genre: Optional[str] = None,
    fromYear: Optional[str] = None,
    toYear: Optional[str] = None,
    session: Session = Depends(db.get_session),
) -> JSONResponse:
    service = service_layer.TrackService(session)
    tracks = service.get_random_songs(size, genre, fromYear, toYear)
    if tracks is None:
        return JSONResponse({"detail": "No page found"}, status_code=404)

    rsp = SubsonicResponse()
    rsp.data["randomSongs"] = OpenSubsonicFormatter.format_tracks(tracks)
    return rsp.to_json_rsp()


@open_subsonic_router.get("/getArtist")
def get_artist(id: int, session: Session = Depends(db.get_session)) -> JSONResponse:
    service = service_layer.ArtistService(session)
    artist: Optional[dto.Artist] = service.get_artist_by_id(id)
    if artist is None:
        return JSONResponse({"detail": "No such id"}, status_code=404)

    rsp = SubsonicResponse()
    rsp.data["artist"] = OpenSubsonicFormatter.format_artist(artist)
    return rsp.to_json_rsp()


@open_subsonic_router.get("/getAlbum")
def get_album(id: int, session: Session = Depends(db.get_session)) -> JSONResponse:
    service = service_layer.AlbumService(session)
    album = service.get_album_by_id(id)
    if album is None:
        return JSONResponse({"detail": "No such id"}, status_code=404)

    rsp = SubsonicResponse()
    rsp.data["album"] = OpenSubsonicFormatter.format_album(album)
    return rsp.to_json_rsp()


@open_subsonic_router.get("/getPlaylist")
def get_playlist(id: int, session: Session = Depends(db.get_session)) -> JSONResponse:
    service = service_layer.PlaylistService(session)
    playlist: dto.Playlist | None = service.get_playlist(id)
    if playlist is None:
        return JSONResponse({"detail": "No such id"}, status_code=404)

    rsp = SubsonicResponse()
    rsp.data["playlist"] = OpenSubsonicFormatter.format_playlist(playlist)
    return rsp.to_json_rsp()


@open_subsonic_router.get("/createPlaylist")
def create_playlist(
    name: str,
    songId: List[int] = Query(default=[]),
    playlistId: int = 0,
    current_user: db.User = Depends(authenticate_user),
    session: Session = Depends(db.get_session),
) -> JSONResponse:
    service = service_layer.PlaylistService(session)
    playlist: dto.Playlist = service.create_playlist(name, songId, current_user)

    rsp = SubsonicResponse()
    rsp.data["playlist"] = OpenSubsonicFormatter.format_playlist(playlist)
    return rsp.to_json_rsp()


@open_subsonic_router.get("/deletePlaylist")
def delete_playlist(
    id: int,
    current_user: db.User = Depends(authenticate_user),
    session: Session = Depends(db.get_session),
) -> JSONResponse:
    if id not in [i.id for i in current_user.playlists]:
        return JSONResponse(
            {
                "detail": f"""You do not have permission to perform this operation. 
                {current_user.login} is not the owner of the playlist."""
            },
            status_code=403,
        )
    service = service_layer.PlaylistService(session)
    service.delete_playlist(id, current_user)
    rsp = SubsonicResponse()
    return rsp.to_json_rsp()


@open_subsonic_router.get("/updatePlaylist")
def update_playlist(
    playlistId: int,
    name: str = "",
    songIdToAdd: List[int] = Query(default=[]),
    songIdToRemove: List[int] = Query(default=[]),
    comment: str = "",
    public: str = "",
    current_user: db.User = Depends(authenticate_user),
    session: Session = Depends(db.get_session),
) -> JSONResponse:
    if playlistId not in [i.id for i in current_user.playlists]:
        return JSONResponse(
            {
                "detail": f"""You do not have permission to perform this operation. 
            {current_user.login} is not the owner of the playlist."""
            },
            status_code=403,
        )
    service = service_layer.PlaylistService(session)
    success: bool = service.update_playlist(
        playlistId, name, songIdToAdd, songIdToRemove
    )
    if not success:
        return JSONResponse({"detail": "No such id"}, status_code=404)
    rsp = SubsonicResponse()
    return rsp.to_json_rsp()


@open_subsonic_router.get("/getIndexes")
def get_indexes(
    musicFolderId: str = Query(default=""),
    ifModifiedSince: int = Query(default=0),
    session: Session = Depends(db.get_session),
) -> JSONResponse:
    index_service = service_layer.IndexService(session)

    indexes: dto.Indexes = index_service.get_indexes_artists(
        musicFolderId, ifModifiedSince, with_childs=True
    )

    rsp = SubsonicResponse()
    rsp.data["indexes"] = OpenSubsonicFormatter.format_indexes(indexes)
    return rsp.to_json_rsp()


@open_subsonic_router.get("/getArtists")
def get_artists(
    musicFolderId: str = Query(default=""),
    session: Session = Depends(db.get_session),
) -> JSONResponse:
    index_service = service_layer.IndexService(session)

    indexes: dto.Indexes = index_service.get_indexes_artists(
        musicFolderId, with_childs=False
    )

    rsp = SubsonicResponse()
    rsp.data["artists"] = OpenSubsonicFormatter.format_indexes(indexes)
    return rsp.to_json_rsp()


@open_subsonic_router.get("/star")
def star(
    id: List[int] = Query(default=[]),
    albumId: List[int] = Query(default=[]),
    artistId: List[int] = Query(default=[]),
    playlistId: List[int] = Query(default=[]),
    current_user: db.User = Depends(authenticate_user),
    session: Session = Depends(db.get_session),
) -> JSONResponse:
    service = service_layer.StarService(session)
    service.star(id, albumId, artistId, playlistId, current_user)
    rsp = SubsonicResponse()
    return rsp.to_json_rsp()


@open_subsonic_router.get("/unstar")
def unstar(
    id: List[int] = Query(default=[]),
    albumId: List[int] = Query(default=[]),
    artistId: List[int] = Query(default=[]),
    playlistId: List[int] = Query(default=[]),
    current_user: db.User = Depends(authenticate_user),
    session: Session = Depends(db.get_session),
) -> JSONResponse:
    service = service_layer.StarService(session)
    service.unstar(id, albumId, artistId, playlistId, current_user)
    rsp = SubsonicResponse()
    return rsp.to_json_rsp()


@open_subsonic_router.get("/getStarred")
def get_starred(
    musicFolderId: int = 0,
    current_user: db.User = Depends(authenticate_user),
    session: Session = Depends(db.get_session),
) -> JSONResponse:
    service = service_layer.StarService(session)
    tracks, albums, artists, playlists = service.get_starred(current_user)
    rsp = SubsonicResponse()
    rsp.data["starred"] = OpenSubsonicFormatter.format_combination(
        artists, albums, tracks, playlists
    )
    return rsp.to_json_rsp()


@open_subsonic_router.get("/getStarred2")
def get_starred2(
    musicFolderId: int = 0,
    current_user: db.User = Depends(authenticate_user),
    session: Session = Depends(db.get_session),
) -> JSONResponse:
    service = service_layer.StarService(session)
    tracks, albums, artists, playlists = service.get_starred(current_user)
    rsp = SubsonicResponse()
    rsp.data["starred2"] = OpenSubsonicFormatter.format_combination(
        artists, albums, tracks, playlists
    )
    return rsp.to_json_rsp()


@open_subsonic_router.get("/startScan")
async def start_scan(session: Session = Depends(db.get_session)) -> JSONResponse:
    db_loading.scanStatus["scanning"] = True
    db_loading.scanStatus["count"] = 0

    utils.clear_tables(session)
    asyncio.get_running_loop().run_in_executor(None, db_loading.scan_and_load)

    rsp = SubsonicResponse()
    rsp.data["scanStatus"] = db_loading.scanStatus
    return rsp.to_json_rsp()


@open_subsonic_router.get("/getScanStatus")
def get_scan_status() -> JSONResponse:
    rsp = SubsonicResponse()
    rsp.data["scanStatus"] = db_loading.scanStatus
    return rsp.to_json_rsp()


@open_subsonic_router.get("/getAlbumList")
def get_album_list(
    type: str,
    size: int = 10,
    offset: int = 0,
    fromYear: Optional[str] = None,
    toYear: Optional[str] = None,
    genre: Optional[str] = None,
    musicFolderId: Optional[str] = None,
    session: Session = Depends(db.get_session),
) -> JSONResponse:
    album_service = service_layer.AlbumService(session)

    request_type: service_layer.RequestType = service_layer.RequestType.BY_NAME
    match type:
        case "random":
            request_type = service_layer.RequestType.RANDOM
        case "alphabeticalByName":
            request_type = service_layer.RequestType.BY_NAME
        case "alphabeticalByArtist":
            request_type = service_layer.RequestType.BY_ARTIST
        case "byYear":
            request_type = service_layer.RequestType.BY_YEAR
        case "newest" | "highest" | "frequent" | "recent" | "byGenre":
            # Not implemented
            request_type = service_layer.RequestType.BY_NAME
        case _:
            return JSONResponse({"detail": "Invalid arguments"}, status_code=400)

    albums = album_service.get_album_list(
        request_type, size, offset, fromYear, toYear, genre, musicFolderId
    )
    if albums is None:
        return JSONResponse({"detail": "Invalid arguments"}, status_code=400)

    rsp = SubsonicResponse()
    rsp.data["albumList"] = OpenSubsonicFormatter.format_albums(albums)
    return rsp.to_json_rsp()


@open_subsonic_router.get("/getAlbumList2")
def get_album_list2(
    type: str,
    size: int = 10,
    offset: int = 0,
    fromYear: Optional[str] = None,
    toYear: Optional[str] = None,
    genre: Optional[str] = None,
    musicFolderId: Optional[str] = None,
    session: Session = Depends(db.get_session),
) -> JSONResponse:
    album_service = service_layer.AlbumService(session)

    request_type: service_layer.RequestType = service_layer.RequestType.BY_NAME
    match type:
        case "random":
            request_type = service_layer.RequestType.RANDOM
        case "alphabeticalByName":
            request_type = service_layer.RequestType.BY_NAME
        case "alphabeticalByArtist":
            request_type = service_layer.RequestType.BY_ARTIST
        case "byYear":
            request_type = service_layer.RequestType.BY_YEAR
        case "newest" | "highest" | "frequent" | "recent" | "byGenre":
            # Not implemented
            request_type = service_layer.RequestType.BY_NAME
        case _:
            return JSONResponse({"detail": "Invalid arguments"}, status_code=400)

    albums = album_service.get_album_list(
        request_type, size, offset, fromYear, toYear, genre, musicFolderId
    )
    if albums is None:
        return JSONResponse({"detail": "Invalid arguments"}, status_code=400)

    rsp = SubsonicResponse()
    rsp.data["albumList2"] = OpenSubsonicFormatter.format_albums(albums)
    return rsp.to_json_rsp()


@open_subsonic_router.get("/getOpenSubsonicExtensions")
def get_open_subsonic_extensions() -> JSONResponse:
    rsp = SubsonicResponse()
    rsp.data["openSubsonicExtensions"] = [
        {"name": "songLyrics", "versions": [1]},
    ]
    return rsp.to_json_rsp()


@open_subsonic_router.get("/getMusicFolders")
def get_music_folders() -> JSONResponse:
    rsp = SubsonicResponse()
    rsp.data["musicFolders"] = {"musicFolder": [{"id": 1, "name": "tracks"}]}
    return rsp.to_json_rsp()


@open_subsonic_router.get("/getLyricsBySongId")
def get_lyrics_by_song_id(
    id: int, session: Session = Depends(db.get_session)
) -> JSONResponse:
    service = service_layer.TrackService(session)
    lyrics_list = service.extract_lyrics(id)
    if lyrics_list is None:
        return JSONResponse({"detail": "No such a song"}, status_code=404)
    lyrics_res = []
    for lyrics in lyrics_list:
        lyrics_res.append(
            {
                "lang": lyrics.get("lang", "xxx"),
                "offset": 0,
                "synced": False,
                "line": [{"value": i} for i in lyrics.get("text", [])],
            }
        )
    rsp = SubsonicResponse()
    rsp.data["lyricsList"] = {"structuredLyrics": lyrics_res}
    return rsp.to_json_rsp()


@open_subsonic_router.get("/getCoverArt")
def get_cover_art(
    id: str, size: int | None = None, session: Session = Depends(db.get_session)
) -> Response:
    image_bytes: bytes | None = None

    prefix, right = id.split("-")
    if not right.isdigit():
        return JSONResponse({"detail": "Invalid id"}, status_code=400)
    parsed_id = int(right)

    if prefix == "mf":
        track = session.exec(
            select(db.Track).where(db.Track.id == parsed_id)
        ).one_or_none()
        if track is None:
            return JSONResponse({"detail": "No such track id"}, status_code=404)
        audio, _ = utils.get_audio_object(track)
        image_bytes = utils.get_cover_from_audio(audio)

    elif prefix == "al":
        album = session.exec(
            select(db.Album).where(db.Album.id == parsed_id)
        ).one_or_none()
        if album is None:
            return JSONResponse({"detail": "No such album id"}, status_code=404)

        album_helpers = db_helpers.AlbumDBHelper(session)
        track = album_helpers.get_first_track(album.id)
        if track is None:
            return JSONResponse({"detail": "No such track id"}, status_code=404)
        audio, _ = utils.get_audio_object(track)
        image_bytes = utils.get_cover_from_audio(audio)

    elif prefix == "ar":
        artist = session.exec(
            select(db.Artist).where(db.Artist.id == parsed_id)
        ).one_or_none()
        if artist is None:
            return JSONResponse({"detail": "No such artist id"}, status_code=404)

    else:
        return JSONResponse({"detail": "No such prefix"}, status_code=404)

    image: Image.Image
    if image_bytes is None:
        image = Image.open(utils.DEFAULT_COVER_PATH)
        image_bytes = utils.image_to_bytes(image)
    else:
        image = utils.bytes_to_image(image_bytes)

    if size is not None:
        if size <= 0:
            return JSONResponse({"detail": "Invalid size"}, status_code=400)
        image.thumbnail((size, size))
        image_bytes = utils.image_to_bytes(image)

    return Response(
        content=image_bytes, media_type=f"image/{str(image.format).lower()}"
    )


@open_subsonic_router.get("/getAvatar")
def get_avatar(
    username: str,
    current_user: db.User = Depends(authenticate_user),
    session: Session = Depends(db.get_session),
) -> Response:
    user = service_layer.get_user_by_username(session, username)
    if not user:
        return JSONResponse({"detail": "No such user"}, status_code=404)

    avatar = service_layer.get_avatar(user)
    return Response(content=avatar, media_type="image/png")
