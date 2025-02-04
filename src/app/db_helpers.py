from sqlmodel import Session, select
from sqlalchemy import func
from . import database as db


class ArtistDBHelper:
    def __init__(self, session: Session):
        self.session = session

    def get_all_artists(self, filter_name=None):
        if filter_name:
            return self.session.exec(
                select(db.Artist).where(
                    func.lower(db.Artist.name).like(f"%{filter_name.lower()}%")
                )
            ).all()
        return self.session.exec(select(db.Artist)).all()

    def get_artist_by_id(self, id):
        return self.session.exec(
            select(db.Artist).where(db.Artist.id == id)
        ).one_or_none()


class AlbumDBHelper:
    def __init__(self, session: Session):
        self.session = session

    def get_all_albums(self, filter_name=None):
        if filter_name:
            return self.session.exec(
                select(db.Album).where(
                    func.lower(db.Album.name).like(f"%{filter_name.lower()}%")
                )
            ).all()
        return self.session.exec(select(db.Album)).all()

    def get_album_by_id(self, id):
        return self.session.exec(
            select(db.Album).where(db.Album.id == id)
        ).one_or_none()


class TrackDBHelper:
    def __init__(self, session: Session):
        self.session = session

    def get_all_tracks(self, filter_title=None):
        if filter_title:
            return self.session.exec(
                select(db.Track).where(
                    func.lower(db.Track.title).like(f"%{filter_title.lower()}%")
                )
            ).all()
        return self.session.exec(select(db.Track)).all()

    def get_track_by_id(self, id):
        return self.session.exec(
            select(db.Track).where(db.Track.id == id)
        ).one_or_none()

    def get_track_by_artist_id(self, artist_id):
        return self.session.exec(
            select(db.Track)
            .join(db.ArtistTrack)
            .where(db.ArtistTrack.artist_id == artist_id)
        ).all()


class GenresDBHelper:
    def __init__(self, session: Session):
        self.session = session

    def get_genres_by_name(self, filter_name=None):
        if filter_name:
            return self.session.exec(
                select(db.Genre).where(func.lower(db.Genre.name) == filter_name.lower())
            ).all()
        return self.session.exec(select(db.Genre)).all()

    def get_all_genres(self, filter_name=None):
        if filter_name:
            return self.session.exec(
                select(db.Genre).where(
                    func.lower(db.Genre.name).like(f"%{filter_name.lower()}%")
                )
            ).all()
        return self.session.exec(select(db.Genre)).all()

    def get_track_by_name(self, name):
        return self.session.exec(
            select(db.Genre).where(db.Genre.name == name)
        ).one_or_none()
