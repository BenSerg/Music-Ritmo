import logging
import os
import re
from enum import StrEnum

from pathlib import Path
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from sqlmodel import Session, select

from . import database as db
from .utils import (
    create_default_user,
    get_cover_from_mp3,
    get_cover_from_flac,
    get_cover_preview,
)


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

scanStatus = {"scanning": True, "count": 0}


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
        album_artist: str | None,
        album: str,
        genres: list[str],
        track_number: int | None,
        year: int | None,
        cover: bytes,
        cover_type: str,
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
        self.album_artist = album_artist
        self.album = album
        self.genres = genres
        self.track_number = track_number
        self.year = year
        self.cover = cover
        self.cover_type = cover_type
        self.bit_rate = bit_rate
        self.bits_per_sample = bits_per_sample
        self.sample_rate = sample_rate
        self.channels = channels
        self.duration = duration


def extract_metadata_mp3(file_path):
    audio_file = MP3(file_path)
    cover, cover_type = get_cover_preview(get_cover_from_mp3(audio_file))
    return AudioInfo(
        file_path=file_path,
        file_size=os.path.getsize(file_path),
        type="audio/mpeg",
        title=(
            str(audio_file["TIT2"])
            if "TIT2" in audio_file.tags
            else Path(file_path).stem
        ),
        artists=(
            re.split(r"[;,\\]\s*", str(audio_file["TPE1"]))
            if "TPE1" in audio_file.tags
            else ["Неизвестный исполнитель"]
        ),
        album_artist=(
            str(audio_file["TPE2"]).split(", ")[0]
            if "TPE2" in audio_file.tags
            else None
        ),
        album=(
            str(audio_file["TALB"])
            if "TALB" in audio_file.tags
            else "Неизвестный альбом"
        ),
        genres=(
            re.split(r"[;,\\]\s*", str(audio_file["TCON"]))
            if "TCON" in audio_file.tags
            else []
        ),
        track_number=(
            int(str(audio_file["TRCK"])) if "TRCK" in audio_file.tags else None
        ),
        year=int(str(audio_file["TDRC"])) if "TDRC" in audio_file.tags else None,
        cover=cover,
        cover_type=cover_type,
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
    cover, cover_type = get_cover_preview(get_cover_from_flac(audio_file))
    return AudioInfo(
        file_path=file_path,
        file_size=os.path.getsize(file_path),
        type="audio/flac",
        title=(
            str(audio_file["TITLE"][0])
            if "TITLE" in audio_file.tags
            else Path(file_path).stem
        ),
        artists=(
            audio_file["ARTIST"]
            if "ARTIST" in audio_file.tags
            else ["Неизвестный исполнитель"]
        ),
        album_artist=(
            audio_file["ALBUMARTIST"][0] if "ALBUMARTIST" in audio_file.tags else None
        ),
        album=(
            str(audio_file["ALBUM"][0])
            if "ALBUM" in audio_file.tags
            else "Неизвестный альбом"
        ),
        genres=(audio_file["GENRE"] if "GENRE" in audio_file.tags else []),
        track_number=(
            int(str(audio_file["TRACKNUMBER"][0]))
            if "TRACKNUMBER" in audio_file.tags
            else None
        ),
        year=int(str(audio_file["DATE"][0]).split('-')[0]) if "DATE" in audio_file.tags else None,
        cover=cover,
        cover_type=cover_type,
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
            ).one_or_none()
            if artist is None:
                artist = db.Artist(name=name)
                session.add(artist)
                session.commit()
                session.refresh(artist)
            artists.append(artist)

        album_artists = []
        album_artist_id: int | None = None
        if audio.album_artist is not None and audio.album_artist != "Various Artists":
            album_artist = session.exec(
                select(db.Artist).where(db.Artist.name == audio.album_artist)
            ).one_or_none()
            if album_artist is None:
                album_artist = db.Artist(name=audio.album_artist)
                session.add(album_artist)
                session.commit()
                session.refresh(album_artist)
            album_artist_id = album_artist.id
            album_artists = [album_artist]
        else:
            album_artists = artists

        album = session.exec(
            select(db.Album).where(db.Album.name == audio.album)
        ).one_or_none()
        if album is None:
            album = db.Album(
                name=audio.album,
                album_artist_id=album_artist_id,
                total_tracks=1,
                year=audio.year,
                cover=audio.cover,
                artists=album_artists,
            )
            session.add(album)
            session.commit()
            session.refresh(album)
        elif album.album_artist_id is None:
            if album_artist_id is not None:
                album.album_artist_id = album_artist_id
            else:
                album.artists = list(set(album.artists).union(artists))
        elif album_artist_id is not None and album.album_artist_id != album_artist_id:
            album.album_artist_id = album_artist_id

        genres = []
        for name in audio.genres:
            genre = session.exec(
                select(db.Genre).where(db.Genre.name == name)
            ).one_or_none()
            if genre is None:
                genre = db.Genre(name=name)
                session.add(genre)
                session.commit()
                session.refresh(genre)
            genres.append(genre)

        track = session.exec(
            select(db.Track).where(db.Track.file_path == audio.file_path)
        ).one_or_none()
        if track is None:
            track = db.Track(
                file_path=audio.file_path,
                file_size=audio.file_size,
                type=audio.type,
                title=audio.title,
                album_id=album.id,
                album_artist_id=album_artist_id,
                album_position=audio.track_number,
                year=audio.year,
                plays_count=0,
                cover=audio.cover,
                cover_type=audio.cover_type,
                bit_rate=audio.bit_rate,
                bits_per_sample=audio.bits_per_sample,
                sample_rate=audio.sample_rate,
                channels=audio.channels,
                duration=audio.duration,
                genres=genres,
                artists=artists,
            )
            album.total_tracks = album.total_tracks + 1
        else:
            track.title = audio.title
            track.artists = artists
            track.album_id = album.id
            track.album_artist_id = album_artist_id
            track.album_position = audio.track_number
            track.year = audio.year
            track.genres = genres

        session.add(track)
        session.commit()
        session.refresh(track)


def scan_and_load(directory_path: str = "./tracks/"):
    audio_files = scan_directory_for_audio_files(directory_path)
    for file in audio_files:
        load_audio_data(file)
        scanStatus["count"] = scanStatus["count"] + 1

    scanStatus["scanning"] = False
