from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from . import database as db


def decode_password(p: str) -> tuple[str | None, bool]:
    password: str = ""
    if p.startswith("enc"):
        if len(p) < 4:
            return None, True
        enc_pass = bytes.fromhex(p[4:])
        password = enc_pass.decode("utf-8")
    else:
        password = p

    return password, False


auth_router = APIRouter(prefix="")


@auth_router.get("/authenticate_user")  # tmp
def authenticate_user(
    u: str = Query(None),
    p: str = Query(None),
    session: Session = Depends(db.get_session),
) -> db.User:
    user = session.exec(select(db.User).where(db.User.login == u)).first()

    password, err = decode_password(p)

    if not user or err or user.password != password:
        raise HTTPException(status_code=401, detail="Wrong username or password")

    return user
