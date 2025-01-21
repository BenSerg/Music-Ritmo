from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from . import database as db

router = APIRouter()

@router.post("/users/")
def add_user(user: db.User, session: Session = Depends(db.get_session)):
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@router.post("/tracks/")
def add_track(track: db.Track, session: Session = Depends(db.get_session)):
    session.add(track)
    session.commit()
    session.refresh(track)
    return track

@router.post("/albums/")
def add_album(album: db.Album, session: Session = Depends(db.get_session)):
    session.add(album)
    session.commit()
    session.refresh(album)
    return album

@router.post("/genres/")
def add_genre(genre: db.Genre, session: Session = Depends(db.get_session)):
    session.add(genre)
    session.commit()
    session.refresh(genre)
    return genre

@router.post("/tracks/{track_id}/genres/{genre_id}")
def add_track_genre(track_id: int, genre_id: int, session: Session = Depends(db.get_session)):
    track_genre = db.GenreTrack(genre_id=genre_id, track_id=track_id)
    session.add(track_genre)
    session.commit()
    session.refresh(track_genre)
    return track_genre

@router.post("/users/{user_id}/favourite/tracks/{track_id}")
def add_favourite_track(user_id: int, track_id: int, session: Session = Depends(db.get_session)):
    favourite_track = db.FavouriteTrack(user_id=user_id, track_id=track_id, added_at="23:59")
    session.add(favourite_track)
    session.commit()
    session.refresh(favourite_track)
    return favourite_track


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