from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field
from sqlmodel import Session, select
from . import database as db

login_router = APIRouter()

class LoginRequest(BaseModel):
    login: str = Field(..., min_length=5, max_length=64)
    password: str = Field(..., min_length=5, max_length=64)

@login_router.post("/login/")
def signin(
    login_data: LoginRequest,
    session: Session = Depends(db.get_session)
):
    login = login_data.login
    password = login_data.password

    statement = select(db.User).where(db.User.login == login)
    user = session.exec(statement).first()

    if not user or user.password != password:
        raise HTTPException(status_code=401, detail="Wrong login/password")

    return RedirectResponse(url="/", status_code=303)
