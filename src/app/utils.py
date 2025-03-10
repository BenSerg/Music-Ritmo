import re
from typing import Any, cast
from PIL import Image
from io import BytesIO

from enum import Enum
from mutagen.id3 import TXXX, TIT2, TPE1, TPE2, TALB, TCON, TRCK, TDRC  # type: ignore[attr-defined]
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from sqlmodel import Session, select

from src.app import database as db

TAG_MULTIPLE_PATTERN = r"[;,\\]\s*"

MAX_COVER_PREVIEW_SIZE = 128
DEFAULT_COVER_PREVIEW_PATH = "./resources/default_cover_preview.jpg"
DEFAULT_COVER_PATH = "./resources/default_cover.jpg"


class AudioType(Enum):
    MP3 = (1,)
    FLAC = (2,)


def bytes_to_image(image_bytes: bytes) -> Image.Image:
    return cast(Image.Image, Image.open(BytesIO(image_bytes)))


def image_to_bytes(image: Image.Image) -> bytes:
    buf = BytesIO()
    image.save(buf, format=image.format)
    return buf.getvalue()


def get_cover_preview(image_bytes: bytes | None) -> tuple[bytes, str]:
    if image_bytes is None:
        default_image = Image.open(DEFAULT_COVER_PREVIEW_PATH)
        return image_to_bytes(default_image), str(default_image.format).lower()

    image = bytes_to_image(image_bytes)
    width, height = image.size
    if width <= MAX_COVER_PREVIEW_SIZE and height <= MAX_COVER_PREVIEW_SIZE:
        return image_bytes, str(image.format).lower()

    image.thumbnail((MAX_COVER_PREVIEW_SIZE, MAX_COVER_PREVIEW_SIZE))
    return image_to_bytes(image), str(image.format).lower()


def get_cover_from_audio(audio: MP3 | FLAC) -> bytes | None:
    cover: bytes | None = None
    match audio:
        case MP3():
            tags = audio.tags
            if tags is not None and "APIC:3.jpeg" in tags:
                cover = bytes(tags["APIC:3.jpeg"].data)
        case FLAC():
            cover = audio.pictures[0].data if len(audio.pictures) > 0 else None
    return cover


def get_audio_object(track: db.Track) -> tuple[MP3 | FLAC, AudioType]:
    match track.type:
        case "audio/mpeg":
            return MP3(track.file_path), AudioType.MP3
        case "audio/flac":
            return FLAC(track.file_path), AudioType.FLAC
        case _:
            assert False, f"Unexpected track type: {track.type}"


def popTag(
    audio: MP3 | FLAC, audio_type: AudioType, tag_names: dict[AudioType, str]
) -> None:
    if tag_names[audio_type] in (audio.tags or []):
        audio.pop(tag_names[audio_type])


def update_tags(track: db.Track, tags: dict[str, Any]) -> tuple[MP3 | FLAC, AudioType]:
    audio, audio_type = get_audio_object(track)

    for key, value in tags.items():
        valueStr = str(value)
        match key:
            case "title":
                match audio_type:
                    case AudioType.MP3:
                        audio["TIT2"] = TIT2(text=[valueStr])  # type: ignore[no-untyped-call]
                    case AudioType.FLAC:
                        audio["TITLE"] = valueStr

            case "artists":
                match audio_type:
                    case AudioType.MP3:
                        audio["TPE1"] = TPE1(text=[valueStr])  # type: ignore[no-untyped-call]
                    case AudioType.FLAC:
                        audio["ARTIST"] = re.split(TAG_MULTIPLE_PATTERN, valueStr)

            case "album_artist":
                if value is None:
                    popTag(
                        audio,
                        audio_type,
                        {AudioType.MP3: "TPE2", AudioType.FLAC: "ALBUMARTIST"},
                    )
                    continue

                match audio_type:
                    case AudioType.MP3:
                        audio["TPE2"] = TPE2(text=[valueStr])  # type: ignore[no-untyped-call]
                    case AudioType.FLAC:
                        audio["ALBUMARTIST"] = valueStr

            case "album":
                match audio_type:
                    case AudioType.MP3:
                        audio["TALB"] = TALB(text=[valueStr])  # type: ignore[no-untyped-call]
                    case AudioType.FLAC:
                        audio["ALBUM"] = valueStr

            case "album_position":
                if value is None:
                    popTag(
                        audio,
                        audio_type,
                        {AudioType.MP3: "TRCK", AudioType.FLAC: "TRACKNUMBER"},
                    )
                    continue

                if valueStr.isdigit():
                    match audio_type:
                        case AudioType.MP3:
                            audio["TRCK"] = TRCK(text=[valueStr])  # type: ignore[no-untyped-call]
                        case AudioType.FLAC:
                            audio["TRACKNUMBER"] = valueStr

            case "year":
                if value is None:
                    popTag(
                        audio,
                        audio_type,
                        {AudioType.MP3: "TDRC", AudioType.FLAC: "DATE"},
                    )
                    continue

                match audio_type:
                    case AudioType.MP3:
                        audio["TDRC"] = TDRC(text=[valueStr])  # type: ignore[no-untyped-call]
                    case AudioType.FLAC:
                        audio["DATE"] = valueStr

            case "genres":
                if value == "":
                    popTag(
                        audio,
                        audio_type,
                        {AudioType.MP3: "TCON", AudioType.FLAC: "GENRE"},
                    )
                    continue

                match audio_type:
                    case AudioType.MP3:
                        audio["TCON"] = TCON(text=[valueStr])  # type: ignore[no-untyped-call]
                    case AudioType.FLAC:
                        audio["GENRE"] = re.split(TAG_MULTIPLE_PATTERN, valueStr)

            case _:
                for tag in track.custom_tags:
                    if tag.name == key:
                        tag.updated = True

                match audio_type:
                    case AudioType.MP3:
                        audio["TXXX:" + key] = TXXX(desc=key, text=valueStr)  # type: ignore[no-untyped-call]
                    case AudioType.FLAC:
                        audio["TXXX:" + str(hash(key))] = key + "; " + valueStr

    for tag in track.custom_tags:
        match audio_type:
            case AudioType.MP3:
                key = "TXXX:" + tag.name
            case AudioType.FLAC:
                key = "TXXX:" + str(hash(tag.name))
        if tag.updated == False and key in (audio.tags or []):
            audio.pop(key)
        tag.updated = False

    return audio, audio_type


def clear_tables(session: Session) -> None:
    for table in [
        db.Album,
        db.Playlist,
        db.Genre,
        db.CustomTag,
        db.Track,
        db.GenreTrack,
        db.ArtistTrack,
        db.ArtistAlbum,
        db.PlaylistTrack,
    ]:
        for row in session.exec(select(table)).all():
            session.delete(row)
    session.commit()


def get_custom_tags(audio_file: MP3 | FLAC) -> list[tuple[str, str]]:
    custom_tags: list[tuple[str, str]] = []
    if audio_file.tags:
        for tag in audio_file.tags:
            if isinstance(audio_file, MP3):
                if str(tag).startswith("TXXX:"):
                    custom_tags.append((audio_file[tag].desc, audio_file[tag].text[0]))
            elif isinstance(audio_file, FLAC):
                key, value = tag
                if str(key).startswith("TXXX:"):
                    custom_tags.append(tuple(value.split("; ")))
    return custom_tags


def get_track_tags(track: db.Track, session: Session) -> dict[str, str]:
    album_artist = ""
    if track.album_artist_id is not None:
        album_artist = (
            session.exec(select(db.Artist).where(db.Artist.id == track.album_artist_id))
            .one()
            .name
        )

    custom_tags = {}
    for tag in track.custom_tags:
        custom_tags[tag.name] = tag.value

    return {
        "title": track.title,
        "artists": ", ".join(artist.name for artist in track.artists),
        "album_artist": album_artist,
        "album": track.album.name,
        "album_position": str(track.album_position),
        "year": str(track.year),
        "genres": ", ".join(genre.name for genre in track.genres),
    } | custom_tags
