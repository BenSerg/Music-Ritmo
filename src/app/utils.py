from PIL import Image
from io import BytesIO

from mutagen.mp3 import MP3
from mutagen.flac import FLAC

MAX_COVER_PREVIEW_SIZE = 128

def bytes_to_image(image_bytes: bytes) -> Image.Image:
    return Image.open(BytesIO(image_bytes))

def image_to_bytes(image: Image.Image) -> bytes:
    buf = BytesIO()
    image.save(buf, format=image.format)
    return buf.getvalue()

def get_cover_preview(image_bytes: bytes | None) -> bytes | None:
    if image_bytes == None:
        return None

    image = bytes_to_image(image_bytes)
    width, height = image.size
    if width <= MAX_COVER_PREVIEW_SIZE and height <= MAX_COVER_PREVIEW_SIZE:
        return image_bytes
    
    image.thumbnail((MAX_COVER_PREVIEW_SIZE, MAX_COVER_PREVIEW_SIZE))
    return image_to_bytes(image)

def get_cover_from_mp3(audio_file_mp3: MP3) -> bytes | None:
    return audio_file_mp3["APIC:3.jpeg"].data if "APIC:3.jpeg" in audio_file_mp3.tags else None

def get_cover_from_flac(audio_file_flac: FLAC) -> bytes | None:
    return audio_file_flac.pictures[0].data if len(audio_file_flac.pictures) > 0 else None
