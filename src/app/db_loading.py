import logging
import os
from enum import StrEnum

from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from sqlmodel import Session, select

from . import database as db
from .utils import get_cover_from_mp3, get_cover_from_flac, get_cover_preview

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class UnknownTag(StrEnum):
    Title = "Unknown Title"
    Artist = "Unknown Artist"
    Album = "Unknown Album"
    Genre = "Unknown Genre"


class AudioInfo:
    def __init__(
        self,
        file_path: str,
        file_size: int,
        type: str,
        title: str,
        artists: list[str],
        album: str,
        genres: list[str],
        track_number: int | None,
        year: int | None,
        cover: bytes | None,
        bit_rate: int,
        bits_per_sample: int,
        sample_rate: int,
        channels: int,
        duration: int,
    ):
        self.file_path = file_path
        self.file_size = file_size
        self.type = type
        self.title = title
        self.artists = artists
        self.album = album
        self.genres = genres
        self.track_number = track_number
        self.year = year
        self.cover = cover
        self.bit_rate = bit_rate
        self.bits_per_sample = bits_per_sample
        self.sample_rate = sample_rate
        self.channels = channels
        self.duration = duration


def extract_metadata_mp3(file_path):
    audio_file = MP3(file_path)
    return AudioInfo(
        file_path=file_path,
        file_size=os.path.getsize(file_path),
        type="audio/mpeg",
        title=(
            str(audio_file["TIT2"]) if "TIT2" in audio_file.tags else UnknownTag.Title
        ),
        artists=(
            str(audio_file["TPE1"]).split(", ")
            if "TPE1" in audio_file.tags
            else [UnknownTag.Artist]
        ),
        album=(
            str(audio_file["TALB"]) if "TALB" in audio_file.tags else UnknownTag.Album
        ),
        genres=(
            str(audio_file["TCON"]).split(", ")
            if "TCON" in audio_file.tags
            else [UnknownTag.Genre]
        ),
        track_number=(
            int(str(audio_file["TRCK"])) if "TRCK" in audio_file.tags else None
        ),
        year=int(str(audio_file["TDRC"])) if "TDRC" in audio_file.tags else None,
        cover=get_cover_preview(get_cover_from_mp3(audio_file)),
        bit_rate=audio_file.info.bitrate,
        bits_per_sample=int(
            audio_file.info.bitrate
            / (audio_file.info.sample_rate * audio_file.info.channels)
        ),
        sample_rate=audio_file.info.sample_rate,
        channels=audio_file.info.channels,
        duration=audio_file.info.length,
    )


def extract_metadata_flac(file_path):
    audio_file = FLAC(file_path)
    return AudioInfo(
        file_path=file_path,
        file_size=os.path.getsize(file_path),
        type="audio/flac",
        title=(
            str(audio_file["TITLE"][0])
            if "TITLE" in audio_file.tags
            else UnknownTag.Title
        ),
        artists=(
            (audio_file["ARTIST"])
            if "ARTIST" in audio_file.tags
            else [UnknownTag.Artist]
        ),
        album=(
            str(audio_file["ALBUM"][0])
            if "ALBUM" in audio_file.tags
            else UnknownTag.Album
        ),
        genres=(
            (audio_file["GENRE"]) if "GENRE" in audio_file.tags else [UnknownTag.Genre]
        ),
        track_number=(
            int(str(audio_file["TRACKNUMBER"][0]))
            if "TRACKNUMBER" in audio_file.tags
            else None
        ),
        year=int(str(audio_file["YEAR"][0])) if "YEAR" in audio_file.tags else None,
        cover=get_cover_preview(get_cover_from_flac(audio_file)),
        bit_rate=audio_file.info.bitrate,
        bits_per_sample=audio_file.info.bits_per_sample,
        sample_rate=audio_file.info.sample_rate,
        channels=audio_file.info.channels,
        duration=audio_file.info.length,
    )


def scan_directory_for_audio_files(dir) -> list[AudioInfo]:
    data = []

    for root, _, files in os.walk(dir):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                if file.lower().endswith(".mp3"):
                    info = extract_metadata_mp3(file_path)
                    logger.info(f"Parsed mp3 file {file_path}")
                elif file.lower().endswith(".flac"):
                    info = extract_metadata_flac(file_path)
                    logger.info(f"Parsed flac file {file_path}")
                else:
                    raise Exception("Unsupported file")

                data.append(info)

            except Exception as e:
                logger.warning(f"Error while parsing file {file_path}: {e}")

    return data


def load_audio_data(audio: AudioInfo):
    with Session(db.engine) as session:
        artists = []
        for name in audio.artists:
            artist = session.exec(
                select(db.Artist).where(db.Artist.name == name)
            ).first()
            if artist is None:
                artist = db.Artist(name=name)
                session.add(artist)
                session.commit()
                session.refresh(artist)
            artists.append(artist)

        album = session.exec(
            select(db.Album).where(db.Album.name == audio.album)
        ).first()
        if album is None:
            album = db.Album(
                name=audio.album,
                total_tracks=1,
                year=audio.year,
                cover=audio.cover,
                artists=artists,
            )
            session.add(album)
            session.commit()
            session.refresh(album)
        else:
            album.total_tracks = album.total_tracks + 1

        genres = []
        for name in audio.genres:
            genre = session.exec(select(db.Genre).where(db.Genre.name == name)).first()
            if genre is None:
                genre = db.Genre(name=name)
                session.add(genre)
                session.commit()
                session.refresh(genre)
            genres.append(genre)

        track = session.exec(
            select(db.Track).where(db.Track.file_path == audio.file_path)
        ).first()
        if track is None:
            track = db.Track(
                file_path=audio.file_path,
                file_size=audio.file_size,
                type=audio.type,
                title=audio.title,
                album_id=album.id,
                album_position=audio.track_number,
                year=audio.year,
                plays_count=0,
                cover=audio.cover,
                bit_rate=audio.bit_rate,
                bits_per_sample=audio.bits_per_sample,
                sample_rate=audio.sample_rate,
                channels=audio.channels,
                duration=audio.duration,
                genres=genres,
                artists=artists,
            )
            session.add(track)
            session.commit()
            session.refresh(track)
