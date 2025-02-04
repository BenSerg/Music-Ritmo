from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from . import database as db

router = APIRouter()


@router.post("/users/")
def add_user(user: db.User, session: Session = Depends(db.get_session)):
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.delete("/users/{user_id}")
def delete_user(user_id: int, session: Session = Depends(db.get_session)):
    user = session.exec(select(db.User).where(db.User.id == user_id)).first()
    if user is None:
        raise HTTPException(status_code=400, detail="Invalid user id")

    session.delete(user)
    session.commit()


@router.post("/playlists/")
def add_playlist(playlist: db.Playlist, session: Session = Depends(db.get_session)):
    session.add(playlist)
    session.commit()
    session.refresh(playlist)
    return playlist


@router.post("/tags/")
def add_tag(tag: db.Tag, session: Session = Depends(db.get_session)):
    session.add(tag)
    session.commit()
    session.refresh(tag)
    return tag


@router.post("/users/{user_id}/favourite/tracks/{track_id}")
def add_favourite_track(
    user_id: int, track_id: int, session: Session = Depends(db.get_session)
):
    user = session.exec(select(db.User).where(db.User.id == user_id)).first()
    if user is None:
        raise HTTPException(status_code=400, detail="Invalid user id")

    track = session.exec(select(db.Track).where(db.Track.id == track_id)).first()
    if track is None:
        raise HTTPException(status_code=400, detail="Invalid track id")

    favourite_track = db.FavouriteTrack(
        user_id=user_id, track_id=track_id, added_at=datetime.now()
    )

    session.add(favourite_track)
    session.commit()
    session.refresh(favourite_track)
    return favourite_track


@router.delete("/users/{user_id}/favourite/tracks/{track_id}")
def delete_favourite_track(
    user_id: int, track_id: int, session: Session = Depends(db.get_session)
):
    favourite_track = session.exec(
        select(db.FavouriteTrack).where(
            db.FavouriteTrack.user_id == user_id
            and db.FavouriteTrack.track_id == track_id
        )
    ).first()
    if favourite_track is None:
        raise HTTPException(status_code=400)

    session.delete(favourite_track)
    session.commit()


@router.get("/tracks/{id}/album")
def get_track_album(id: int, session: Session = Depends(db.get_session)):
    query = select(db.Track).where(db.Track.id == id)
    return session.exec(query).one().album


@router.get("/tracks/{id}/genres")
def get_track_genres(id: int, session: Session = Depends(db.get_session)):
    query = select(db.Track).where(db.Track.id == id)
    return session.exec(query).one().genres


@router.get("/users/{id}/favourite/tracks")
def get_favourite_tracks(id: int, session: Session = Depends(db.get_session)):
    query = select(db.User).where(db.User.id == id)
    favourite_tracks = session.exec(query).one().favourite_tracks
    tracks = []
    for favourite_track in favourite_tracks:
        tracks.append(favourite_track.track)
    return tracks


@router.get("/users/")
def get_users(session: Session = Depends(db.get_session)):
    return session.exec(select(db.User)).all()


@router.get("/tracks/")
def get_tracks(session: Session = Depends(db.get_session)):
    return session.exec(select(db.Track)).all()


@router.get("/artists/")
def get_artists(session: Session = Depends(db.get_session)):
    return session.exec(select(db.Artist)).all()


@router.get("/albums/")
def get_albums(session: Session = Depends(db.get_session)):
    return session.exec(select(db.Album)).all()


@router.get("/playlists/")
def get_playlists(session: Session = Depends(db.get_session)):
    return session.exec(select(db.Playlist)).all()


@router.get("/genres/")
def get_genres(session: Session = Depends(db.get_session)):
    return session.exec(select(db.Genre)).all()


@router.get("/tags/")
def get_tags(session: Session = Depends(db.get_session)):
    return session.exec(select(db.Tag)).all()
