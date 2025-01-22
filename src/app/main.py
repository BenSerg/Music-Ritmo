from fastapi import FastAPI
from .database import init_db
from .db_endpoints import router
from .open_subsonic_api import open_subsonic_router
from .db_loading import scan_directory_for_audio_files, load_audio_data
from .frontend_endpoints import frontend_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [ "http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

audio_files = scan_directory_for_audio_files("./tracks/")
for file in audio_files:
    load_audio_data(file)

app.include_router(router)

app.include_router(open_subsonic_router)

app.include_router(frontend_router)
