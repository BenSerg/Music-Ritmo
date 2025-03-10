import logging
import os
import re

from pathlib import Path
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from sqlmodel import Session, select

from src.app import database as db
from src.app import utils


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

scanStatus = {"scanning": True, "count": 0}


class AudioInfo:
    file_path: str
    file_size: int
    type: str
    title: str
    artists: list[str]
    album_artist: str | None
    album: str
    genres: list[str]
    track_number: int | None
    year: str | None
    cover: bytes
    cover_type: str
    custom_tags: list[tuple[str, str]]
    bit_rate: int
    bits_per_sample: int
    sample_rate: int
    channels: int
    duration: int

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.file_size = os.path.getsize(file_path)


def extract_metadata_mp3(audio_file: MP3, audio_info: AudioInfo) -> None:
    audio_info.type = "audio/mpeg"
    audio_info.title = (
        str(audio_file["TIT2"])
        if "TIT2" in audio_file.tags
        else Path(audio_info.file_path).stem
    )
    audio_info.artists = (
        re.split(utils.TAG_MULTIPLE_PATTERN, str(audio_file["TPE1"]))
        if "TPE1" in audio_file.tags
        else ["Неизвестный исполнитель"]
    )
    audio_info.album_artist = (
        str(audio_file["TPE2"]).split(", ")[0] if "TPE2" in audio_file.tags else None
    )
    audio_info.album = (
        str(audio_file["TALB"]) if "TALB" in audio_file.tags else "Неизвестный альбом"
    )
    audio_info.genres = (
        re.split(utils.TAG_MULTIPLE_PATTERN, str(audio_file["TCON"]))
        if "TCON" in audio_file.tags
        else []
    )
    audio_info.track_number = (
        int(str(audio_file["TRCK"])) if "TRCK" in audio_file.tags else None
    )
    audio_info.year = str(audio_file["TDRC"]) if "TDRC" in audio_file.tags else None
    audio_info.cover, audio_info.cover_type = utils.get_cover_preview(
        utils.get_cover_from_audio(audio_file)
    )
    audio_info.custom_tags = utils.get_custom_tags(audio_file)


def extract_metadata_flac(audio_file: FLAC, audio_info: AudioInfo) -> None:
    audio_info.type = "audio/flac"
    audio_info.title = (
        str(audio_file["TITLE"][0])
        if "TITLE" in audio_file.tags  # type: ignore[operator]
        else Path(audio_info.file_path).stem
    )
    audio_info.artists = (
        audio_file["ARTIST"]
        if "ARTIST" in audio_file.tags  # type: ignore[operator]
        else ["Неизвестный исполнитель"]
    )
    audio_info.album_artist = (
        audio_file["ALBUMARTIST"][0] if "ALBUMARTIST" in audio_file.tags else None  # type: ignore[operator]
    )
    audio_info.album = (
        str(audio_file["ALBUM"][0])
        if "ALBUM" in audio_file.tags  # type: ignore[operator]
        else "Неизвестный альбом"
    )
    audio_info.genres = audio_file["GENRE"] if "GENRE" in audio_file.tags else []  # type: ignore[operator]
    audio_info.track_number = (
        int(str(audio_file["TRACKNUMBER"][0]))
        if "TRACKNUMBER" in audio_file.tags  # type: ignore[operator]
        else None
    )
    audio_info.year = str(audio_file["DATE"][0]) if "DATE" in audio_file.tags else None  # type: ignore[operator]
    audio_info.cover, audio_info.cover_type = utils.get_cover_preview(
        utils.get_cover_from_audio(audio_file)
    )
    audio_info.custom_tags = utils.get_custom_tags(audio_file)


def scan_directory_for_audio_files(dir: str) -> list[AudioInfo]:
    data = []

    for root, _, files in os.walk(dir):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                audio_info = AudioInfo(file_path)

                audio_file: MP3 | FLAC | None = None

                if file.lower().endswith(".mp3"):
                    audio_file = MP3(file_path)
                    extract_metadata_mp3(audio_file, audio_info)
                    audio_info.bits_per_sample = int(
                        audio_file.info.bitrate
                        / (audio_file.info.sample_rate * audio_file.info.channels)
                    )

                    logger.info(f"Parsed mp3 file {file_path}")
                elif file.lower().endswith(".flac"):
                    audio_file = FLAC(file_path)
                    extract_metadata_flac(audio_file, audio_info)
                    audio_info.bits_per_sample = audio_file.info.bits_per_sample

                    logger.info(f"Parsed flac file {file_path}")
                else:
                    raise Exception("Unsupported file")

                audio_info.bit_rate = audio_file.info.bitrate
                audio_info.sample_rate = audio_file.info.sample_rate
                audio_info.channels = audio_file.info.channels
                audio_info.duration = audio_file.info.length

                data.append(audio_info)

            except Exception as e:
                logger.warning(f"Error while parsing file {file_path}: {e}")

    return data


def load_audio_data(audio_info: AudioInfo, session: Session) -> None:
    artists = []
    for name in audio_info.artists:
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
    if (
        audio_info.album_artist is not None
        and audio_info.album_artist != "Various Artists"
    ):
        album_artist = session.exec(
            select(db.Artist).where(db.Artist.name == audio_info.album_artist)
        ).one_or_none()
        if album_artist is None:
            album_artist = db.Artist(name=audio_info.album_artist)
            session.add(album_artist)
            session.commit()
            session.refresh(album_artist)
        album_artist_id = album_artist.id
        album_artists = [album_artist]
    else:
        album_artists = artists

    album = session.exec(
        select(db.Album).where(db.Album.name == audio_info.album)
    ).one_or_none()
    if album is None:
        album = db.Album(
            name=audio_info.album,
            album_artist_id=album_artist_id,
            total_tracks=0,
            year=audio_info.year,
            cover=audio_info.cover,
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
    for name in audio_info.genres:
        genre = session.exec(
            select(db.Genre).where(db.Genre.name == name)
        ).one_or_none()
        if genre is None:
            genre = db.Genre(name=name)
            session.add(genre)
            session.commit()
            session.refresh(genre)
        genres.append(genre)

    custom_tags: list[db.CustomTag] = []
    for name, value in audio_info.custom_tags:
        tag = session.exec(
            select(db.CustomTag)
            .where(db.CustomTag.name == name)
            .where(db.CustomTag.value == value)
        ).one_or_none()
        if tag is None:
            tag = db.CustomTag(name=name, value=value, updated=False)
            session.add(tag)
            session.commit()
            session.refresh(tag)
        custom_tags.append(tag)

    track = session.exec(
        select(db.Track).where(db.Track.file_path == audio_info.file_path)
    ).one_or_none()
    if track is None:
        track = db.Track(
            file_path=audio_info.file_path,
            file_size=audio_info.file_size,
            type=audio_info.type,
            title=audio_info.title,
            album_id=album.id,
            album_artist_id=album_artist_id,
            album_position=audio_info.track_number,
            year=audio_info.year,
            plays_count=0,
            cover=audio_info.cover,
            cover_type=audio_info.cover_type,
            bit_rate=audio_info.bit_rate,
            bits_per_sample=audio_info.bits_per_sample,
            sample_rate=audio_info.sample_rate,
            channels=audio_info.channels,
            duration=audio_info.duration,
            genres=genres,
            artists=artists,
            custom_tags=custom_tags,
        )
        album.total_tracks = album.total_tracks + 1
    else:
        track.title = audio_info.title
        track.artists = artists
        track.album_id = album.id
        track.album_artist_id = album_artist_id
        track.album_position = audio_info.track_number
        track.year = audio_info.year
        track.genres = genres
        track.custom_tags = custom_tags

    session.add(track)
    session.commit()
    session.refresh(track)


def scan_and_load(directory_path: str = "./tracks/") -> None:
    audio_files = scan_directory_for_audio_files(directory_path)

    with Session(db.engine) as session:
        for file in audio_files:
            load_audio_data(file, session)
            scanStatus["count"] = scanStatus["count"] + 1

    scanStatus["scanning"] = False
