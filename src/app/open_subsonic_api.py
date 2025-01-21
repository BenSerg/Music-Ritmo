from fastapi import APIRouter, Body, Depends
from fastapi.responses import JSONResponse
from sqlmodel import Session
from .database import get_session
from .db_endpoints import get_albums, get_artists, get_tracks

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


@open_subsonic_router.get("/ping")
async def ping():
    rsp = SubsonicResponse()
    return rsp.to_json_rsp()

@open_subsonic_router.post("/search")
async def search(query: dict=Body(), session: Session = Depends(get_session)):
    name = query["query"]
    artists = get_artists(session=session)
    albums = get_albums(session=session)
    tracks = get_tracks(session=session)
    searchResult = {}
    searchResult["artists"] = [a.model_dump_json() for a in artists if name in a.name]
    searchResult["tracks"] = [a.model_dump_json() for a in tracks if name in a.name]
    searchResult["albums"] = [a.model_dump_json() for a in albums if name in a.name]
    rsp = SubsonicResponse()
    rsp.data["searchResult"] = searchResult
    return rsp.to_json_rsp()
