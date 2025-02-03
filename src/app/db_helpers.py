from sqlmodel import Session, select, Field
from sqlalchemy import func
from . import database as db


class ArtistDBHelper:
    def __init__(self, session: Session):
        self.session = session

    def getAllArtists(self, filterName=None):
        if filterName:
            return self.session.exec(
                select(db.Artist).where(
                    func.lower(db.Artist.name).like(f"%{filterName.lower()}%")
                )
            ).all()
        return self.session.exec(select(db.Artist)).all()

    def getArtistById(self, id):
        return self.session.exec(
            select(db.Artist).where(db.Artist.id == id)
        ).one_or_none()


class AlbumDBHelper:
    def __init__(self, session: Session):
        self.session = session

    def getAllAlbums(self, filterName=None):
        if filterName:
            return self.session.exec(
                select(db.Album).where(
                    func.lower(db.Album.name).like(f"%{filterName.lower()}%")
                )
            ).all()
        return self.session.exec(select(db.Album)).all()

    def getAlbumById(self, id):
        return self.session.exec(
            select(db.Album).where(db.Album.id == id)
        ).one_or_none()


class TrackDBHelper:
    def __init__(self, session: Session):
        self.session = session

    def getAllTracks(self, filterTitle=None):
        if filterTitle:
            return self.session.exec(
                select(db.Track).where(
                    func.lower(db.Track.title).like(f"%{filterTitle.lower()}%")
                )
            ).all()
        return self.session.exec(select(db.Track)).all()

    def getTrackById(self, id):
        return self.session.exec(
            select(db.Track).where(db.Track.id == id)
        ).one_or_none()

    def getTrackByArtistId(self, artistId):
        return self.session.exec(
            select(db.Track)
            .join(db.ArtistTrack)
            .where(db.ArtistTrack.artist_id == artistId)
        ).all()


class GenresDBHelper:
    def __init__(self, session: Session):
        self.session = session

    def get_genres_by_name(self, filterName=None):
        if filterName:
            return self.session.exec(
                select(db.Genre).where(func.lower(db.Genre.name) == filterName.lower())
            ).all()
        return self.session.exec(select(db.Genre)).all()

    def getAllGenres(self, filterName=None):
        if filterName:
            return self.session.exec(
                select(db.Genre).where(
                    func.lower(db.Genre.name).like(f"%{filterName.lower()}%")
                )
            ).all()
        return self.session.exec(select(db.Genre)).all()

    def getTrackByName(self, name):
        return self.session.exec(
            select(db.Genre).where(db.Genre.name == name)
        ).one_or_none()
