from typing import cast
from PIL import Image
from io import BytesIO

from enum import Enum
from mutagen.id3 import TXXX, TIT2, TPE1, TPE2, TALB, TCON, TRCK, TDRC
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from sqlmodel import Session, select, delete
from src.app import service_layer
from . import database as db

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


def get_default_cover():
    return Image.open(DEFAULT_COVER_PATH)


def get_cover_preview(image_bytes: bytes | None) -> tuple[bytes, str]:
    if image_bytes is None:
        default_image = Image.open(DEFAULT_COVER_PREVIEW_PATH)
        return image_to_bytes(default_image), (default_image.format or "").lower()

    image = bytes_to_image(image_bytes)
    width, height = image.size
    if width <= MAX_COVER_PREVIEW_SIZE and height <= MAX_COVER_PREVIEW_SIZE:
        return image_bytes, (image.format or "").lower()

    image.thumbnail((MAX_COVER_PREVIEW_SIZE, MAX_COVER_PREVIEW_SIZE))
    return image_to_bytes(image), (image.format or "").lower()


def get_cover_from_mp3(audio_file_mp3: MP3) -> bytes | None:
    tags = audio_file_mp3.tags
    if tags is not None and "APIC:3.jpeg" in tags:
        return tags["APIC:3.jpeg"].data
    return None


def get_cover_from_flac(audio_file_flac: FLAC) -> bytes | None:
    return (
        audio_file_flac.pictures[0].data if len(audio_file_flac.pictures) > 0 else None
    )


def get_cover_art(track: db.Track) -> bytes | None:
    if track.type == "audio/mpeg":
        return get_cover_from_mp3(MP3(track.file_path))
    elif track.type == "audio/flac":
        return get_cover_from_flac(FLAC(track.file_path))
    else:
        return None


def get_audio_object(track: db.Track) -> tuple[MP3 | FLAC, AudioType]:
    match track.type:
        case "audio/mpeg":
            return MP3(track.file_path), AudioType.MP3
        case "audio/flac":
            return FLAC(track.file_path), AudioType.FLAC
        case _:
            assert False, f"Unexpected track type: {track.type}"


def update_tags(
    track: db.Track, tags, session: Session
) -> tuple[MP3 | FLAC, AudioType]:
    audio, audio_type = get_audio_object(track)

    for key, value in tags:
        match key:
            case "title":
                if value != track.title:
                    match audio_type:
                        case AudioType.MP3:
                            audio["TIT2"] = TIT2(text=[value])
                        case AudioType.FLAC:
                            audio["TITLE"] = value

            case "artists":
                artists = value.split(", ")
                if set(artists) != set(track.artists):
                    match audio_type:
                        case AudioType.MP3:
                            audio["TPE1"] = TPE1(text=[value])
                        case AudioType.FLAC:
                            audio["ARTIST"] = artists

            case "album_artist":
                album_artist = ""
                if track.album_artist_id is not None:
                    album_artist = (
                        session.exec(
                            select(db.Artist).where(
                                db.Artist.id == track.album_artist_id
                            )
                        )
                        .one()
                        .name
                    )

                if value != album_artist:
                    match audio_type:
                        case AudioType.MP3:
                            audio["TPE2"] = TPE2(text=[value])
                        case AudioType.FLAC:
                            audio["ALBUMARTIST"] = value

            case "album":
                if value != track.album:
                    match audio_type:
                        case AudioType.MP3:
                            audio["TALB"] = TALB(text=[value])
                        case AudioType.FLAC:
                            audio["ALBUM"] = value

            case "album_position":
                if value != track.album_position:
                    match audio_type:
                        case AudioType.MP3:
                            audio["TRCK"] = TRCK(text=[value])
                        case AudioType.FLAC:
                            audio["TRACKNUMBER"] = str(value)

            case "year":
                if value != track.year:
                    match audio_type:
                        case AudioType.MP3:
                            audio["TDRC"] = TDRC(text=[value])
                        case AudioType.FLAC:
                            audio["DATE"] = str(value)

            case "genres":
                genres = value.split(", ")
                if set(genres) != set(track.genres):
                    match audio_type:
                        case AudioType.MP3:
                            audio["TCON"] = TCON(text=[value])
                        case AudioType.FLAC:
                            audio["GENRE"] = genres

            case _:
                found = False
                should_update = False
                for tag in track.tags:
                    if tag.name == key:
                        found = True
                        tag.updated = True
                        if tag.value != value:
                            should_update = True
                            break

                if not found or should_update:
                    match audio_type:
                        case AudioType.MP3:
                            audio["TXXX:" + key] = TXXX(desc=key, text=value)
                        case AudioType.FLAC:
                            audio["TXXX:" + key] = value

    audio.save()
    return audio, audio_type


def create_default_user():
    service_layer.create_user(next(db.get_session()), "admin", "admin")


def clear_table(table, session: Session):
    for row in session.exec(select(table)).all():
        session.delete(row)


def clear_media(session: Session):
    clear_table(db.Album, session)
    clear_table(db.Playlist, session)
    clear_table(db.Genre, session)
    clear_table(db.Tag, session)
    clear_table(db.Track, session)

    clear_table(db.GenreTrack, session)
    clear_table(db.ArtistTrack, session)
    clear_table(db.ArtistAlbum, session)
    clear_table(db.PlaylistTrack, session)
    session.commit()


def get_custom_tags_mp3(audio_file: MP3):
    custom_tags: list[tuple] = []
    if audio_file.tags:
        for tag in audio_file.tags:
            if tag.startswith("TXXX:"):
                custom_tags.append((audio_file[tag].desc, audio_file[tag].text[0]))
    return custom_tags


def get_custom_tags_flac(audio_file: FLAC):
    custom_tags: list[tuple] = []
    if audio_file.tags:
        for key, value in audio_file.tags:
            if key.startswith("TXXX:"):
                custom_tags.append((key.split(":")[-1], value))
    return custom_tags


def clear_outdated_tags(track: db.Track, audio: MP3 | FLAC):
    for tag in track.tags:
        if tag.updated == False:
            audio.pop("TXXX:" + tag.name)
    audio.save()


def get_base_tags(track: db.Track, session: Session):
    album_artist = ""
    if track.album_artist_id is not None:
        album_artist = (
            session.exec(select(db.Artist).where(db.Artist.id == track.album_artist_id))
            .one()
            .name
        )

    return {
        "title": track.title,
        "artists": ", ".join(artist.name for artist in track.artists),
        "album_artist": album_artist,
        "album": track.album.name,
        "album_position": track.album_position,
        "year": track.year,
        "genres": ", ".join(genre.name for genre in track.genres),
    }


def get_custom_tags(track: db.Track):
    custom_tags = {}
    for tag in track.tags:
        custom_tags[tag.name] = tag.value
    return custom_tags
