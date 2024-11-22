from fastapi import FastAPI
from .database import init_db
from .db_endpoints import router

app = FastAPI()

init_db()

app.include_router(router)
