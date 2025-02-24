import pytest
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.id3 import TXXX, TIT2, TPE1, TPE2, TALB, TCON, TRCK, TDRC, APIC  # type: ignore[attr-defined]

from src.app import db_loading


@pytest.mark.parametrize(
    "file_name, file_tags, expected_tags",
    [
        (
            "temp",
            (
                "title",
                "artist1",
                "artist1",
                "album",
                "genre1",
                "1",
                "2020",
            ),
            (
                "title",
                ["artist1"],
                "artist1",
                "album",
                ["genre1"],
                1,
                "2020",
            ),
        ),
        (
            "temp",
            (
                "title",
                "artist1, artist2",
                "artist2",
                "album",
                "genre1, genre2",
                "2",
                "2009-2021",
            ),
            (
                "title",
                ["artist1", "artist2"],
                "artist2",
                "album",
                ["genre1", "genre2"],
                2,
                "2009-2021",
            ),
        ),
        (
            "temp",
            (
                "title",
                "artist1; artist2",
                None,
                "album",
                "genre1; genre2",
                "3",
                "2021-2022",
            ),
            (
                "title",
                ["artist1", "artist2"],
                None,
                "album",
                ["genre1", "genre2"],
                3,
                "2021-2022",
            ),
        ),
        (
            "temp",
            (
                "title",
                "artist1\\artist2",
                "artist3",
                "album",
                "genre1\\genre2",
                "-1",
                "2020",
            ),
            (
                "title",
                ["artist1", "artist2"],
                "artist3",
                "album",
                ["genre1", "genre2"],
                -1,
                "2020",
            ),
        ),
        (
            "temp",
            (
                "title, title2",
                "artist1 artist2",
                "artist3",
                "album",
                "genre1 genre2",
                "-1",
                "2023",
            ),
            (
                "title, title2",
                ["artist1 artist2"],
                "artist3",
                "album",
                ["genre1 genre2"],
                -1,
                "2023",
            ),
        ),
        (
            "temp",
            (None, None, None, None, None, None, None),
            (
                "temp",
                ["Неизвестный исполнитель"],
                None,
                "Неизвестный альбом",
                [],
                None,
                None,
            ),
        ),
    ],
)
def test_extract_metadata_mp3(
    file_name: str,
    file_tags,
    expected_tags,
):
    title, artists, album_artist, album, genres, track_number, year = file_tags
    (
        exp_title,
        exp_artists,
        exp_album_artist,
        exp_album,
        exp_genres,
        exp_track_number,
        exp_year,
    ) = expected_tags

    audio_info = db_loading.AudioInfo()

    audio_info.file_path = file_name
    audio = MP3("tracks\\MACAN_-_I_AM_78125758.mp3")

    if title is not None:
        audio["TIT2"] = TIT2(text=[title])  # type: ignore[no-untyped-call]
    elif "TIT2" in audio.tags:
        audio.pop("TIT2")
    if artists is not None:
        audio["TPE1"] = TPE1(text=[artists])  # type: ignore[no-untyped-call]
    elif "TPE1" in audio.tags:
        audio.pop("TPE1")

    if album_artist is not None:
        audio["TPE2"] = TPE2(text=[album_artist])  # type: ignore[no-untyped-call]
    elif "TPE2" in audio.tags:
        audio.pop("TPE2")

    if album is not None:
        audio["TALB"] = TALB(text=[album])  # type: ignore[no-untyped-call]
    elif "TALB" in audio.tags:
        audio.pop("TALB")

    if genres is not None:
        audio["TCON"] = TCON(text=[genres])  # type: ignore[no-untyped-call]
    elif "TCON" in audio.tags:
        audio.pop("TCON")

    if track_number is not None:
        audio["TRCK"] = TRCK(text=[track_number])  # type: ignore[no-untyped-call]
    elif "TRCK" in audio.tags:
        audio.pop("TRCK")

    if year is not None:
        audio["TDRC"] = TDRC(text=[year])  # type: ignore[no-untyped-call]
    elif "TDRC" in audio.tags:
        audio.pop("TDRC")

    db_loading.extract_metadata_mp3(audio, audio_info)

    assert audio_info.title == exp_title
    assert audio_info.artists == exp_artists
    assert audio_info.album_artist == exp_album_artist
    assert audio_info.album == exp_album
    assert audio_info.genres == exp_genres
    assert audio_info.track_number == exp_track_number
    assert audio_info.year == exp_year


@pytest.mark.parametrize(
    "file_name, file_tags, expected_tags",
    [
        (
            "temp",
            (
                "title",
                "artist1",
                "artist1",
                "album",
                "genre1",
                "1",
                "2020",
            ),
            (
                "title",
                ["artist1"],
                "artist1",
                "album",
                ["genre1"],
                1,
                "2020",
            ),
        ),
        (
            "temp",
            (
                "title",
                ["artist1", "artist2"],
                "artist2",
                "album",
                ["genre1", "genre2"],
                "2",
                "2009-2021",
            ),
            (
                "title",
                ["artist1", "artist2"],
                "artist2",
                "album",
                ["genre1", "genre2"],
                2,
                "2009-2021",
            ),
        ),
        (
            "temp",
            (None, None, None, None, None, None, None),
            (
                "temp",
                ["Неизвестный исполнитель"],
                None,
                "Неизвестный альбом",
                [],
                None,
                None,
            ),
        ),
    ],
)
def test_extract_metadata_flac(
    file_name: str,
    file_tags,
    expected_tags,
):
    title, artists, album_artist, album, genres, track_number, year = file_tags
    (
        exp_title,
        exp_artists,
        exp_album_artist,
        exp_album,
        exp_genres,
        exp_track_number,
        exp_year,
    ) = expected_tags

    audio_info = db_loading.AudioInfo()

    audio_info.file_path = file_name
    audio = FLAC("tracks\\Atomic Heart\\03. Arlekino (Geoffrey Day Remix).flac")

    if title is not None:
        audio["TITLE"] = title
    elif "TITLE" in audio.tags:
        audio.pop("TITLE")

    if artists is not None:
        audio["ARTIST"] = artists
    elif "ARTIST" in audio.tags:
        audio.pop("ARTIST")

    if album_artist is not None:
        audio["ALBUMARTIST"] = album_artist
    elif "ALBUMARTIST" in audio.tags:
        audio.pop("ALBUMARTIST")

    if album is not None:
        audio["ALBUM"] = album
    elif "ALBUM" in audio.tags:
        audio.pop("ALBUM")

    if genres is not None:
        audio["GENRE"] = genres
    elif "GENRE" in audio.tags:
        audio.pop("GENRE")

    if track_number is not None:
        audio["TRACKNUMBER"] = track_number
    elif "TRACKNUMBER" in audio.tags:
        audio.pop("TRACKNUMBER")

    if year is not None:
        audio["DATE"] = year
    elif "DATE" in audio.tags:
        audio.pop("DATE")

    db_loading.extract_metadata_flac(audio, audio_info)

    assert audio_info.title == exp_title
    assert audio_info.artists == exp_artists
    assert audio_info.album_artist == exp_album_artist
    assert audio_info.album == exp_album
    assert audio_info.genres == exp_genres
    assert audio_info.track_number == exp_track_number
    assert audio_info.year == exp_year
