import pytest
import re
from PIL import Image
from typing import Any
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.id3 import TXXX

from src.app import utils
from src.app import database as db

TEST_MP3_FILE = "tracks\\MACAN_-_I_AM_78125758.mp3"
TEST_FLAC_FILE = "tracks\\Atomic Heart\\03. Arlekino (Geoffrey Day Remix).flac"


@pytest.mark.parametrize(
    "size",
    [
        (None),
        ((utils.MAX_COVER_PREVIEW_SIZE - 1, utils.MAX_COVER_PREVIEW_SIZE - 1)),
        ((utils.MAX_COVER_PREVIEW_SIZE, utils.MAX_COVER_PREVIEW_SIZE)),
        ((utils.MAX_COVER_PREVIEW_SIZE + 1, utils.MAX_COVER_PREVIEW_SIZE + 1)),
        ((utils.MAX_COVER_PREVIEW_SIZE + 1, utils.MAX_COVER_PREVIEW_SIZE - 1)),
    ],
)
def test_get_cover_preview(size: tuple[int, int] | None):
    cover_preview = Image.open(utils.DEFAULT_COVER_PREVIEW_PATH)

    if size is None:
        preview_bytes, format = utils.get_cover_preview(None)

        assert preview_bytes == utils.image_to_bytes(cover_preview)
        assert format == str(cover_preview.format).lower()

    else:
        cover = utils.get_default_cover()
        cover.thumbnail(size)
        preview_bytes, format = utils.get_cover_preview(utils.image_to_bytes(cover))
        preview_image = utils.bytes_to_image(preview_bytes)
        width, height = preview_image.size

        assert (
            width <= utils.MAX_COVER_PREVIEW_SIZE
            and height <= utils.MAX_COVER_PREVIEW_SIZE
        )
        assert format == str(cover_preview.format).lower()


@pytest.mark.parametrize(
    "custom_tags",
    [
        ([]),
        ([("custom1", "value1")]),
        (
            [
                ("custom1", "value1"),
                ("custom2", "value2"),
                ("custom3", "value3"),
                ("custom4", "value1"),
            ]
        ),
    ],
)
def test_get_custom_tags(custom_tags: list[tuple[str, str]]) -> None:
    audio_mp3 = MP3(TEST_MP3_FILE)
    audio_flac = FLAC(TEST_FLAC_FILE)

    for tag in audio_mp3.tags:
        if str(tag).startswith("TXXX:"):
            audio_mp3.pop(tag)
    for tag in audio_flac.tags:
        if str(tag).startswith("TXXX:"):
            audio_flac.pop(tag)

    for key, value in custom_tags:
        audio_mp3["TXXX:" + key] = TXXX(desc=key, text=value)  # type: ignore[no-untyped-call]
        audio_flac["TXXX:" + key] = value

    assert set(utils.get_custom_tags_mp3(audio_mp3)) == set(custom_tags)
    assert set(utils.get_custom_tags_flac(audio_flac)) == set(custom_tags)


@pytest.mark.parametrize(
    "new_tags, expected_tags",
    [
        (
            {
                "title": "new_title",
                "artists": "new_artsit1",
                "album_artist": "new_artist1",
                "album": "new_album1",
                "genres": "new_genre1",
                "album_position": "5",
                "year": "2025",
                "new_custom1": "new_value1",
            },
            (
                "new_title",
                ["new_artsit1"],
                "new_artist1",
                "new_album1",
                ["new_genre1"],
                5,
                "2025",
                [("new_custom1", "new_value1")],
            ),
        ),
        (
            {
                "title": "Present",
                "artists": "present_artist1",
                "album_artist": None,
                "album": "present_album1",
                "genres": "present_genre1",
                "album_position": "2",
                "year": "2019",
                "present_custom1": "present_value1",
            },
            (
                "Present",
                ["present_artist1"],
                None,
                "present_album1",
                ["present_genre1"],
                2,
                "2019",
                [("present_custom1", "present_value1")],
            ),
        ),
        (
            {
                "title": "Present",
                "artists": "present_artist1",
                "album_artist": None,
                "album": "present_album1",
                "genres": "",
                "album_position": None,
                "year": None,
            },
            (
                "Present",
                ["present_artist1"],
                None,
                "present_album1",
                [],
                None,
                None,
                [],
            ),
        ),
        (
            {
                "title": "Present",
                "artists": "present_artist1; new_artist1, new_artist2",
                "album_artist": None,
                "album": "present_album1",
                "genres": "present_genre1; new_genre1, new_genre2",
                "album_position": "2",
                "year": "2020",
                "new_custom1": "new_value1",
                "present_custom1": "present_value1",
            },
            (
                "Present",
                ["present_artist1", "new_artist1", "new_artist2"],
                None,
                "present_album1",
                ["present_genre1", "new_genre1", "new_genre2"],
                2,
                "2020",
                [("present_custom1", "present_value1"), ("new_custom1", "new_value1")],
            ),
        ),
    ],
)
def test_update_tags(new_tags: dict[str, Any], expected_tags) -> None:
    (
        exp_title,
        exp_artists,
        exp_album_artist,
        exp_album,
        exp_genres,
        exp_track_number,
        exp_year,
        exp_custom,
    ) = expected_tags

    track_mp3 = db.Track(
        file_path=TEST_MP3_FILE,
        file_size=3,
        type="audio/mpeg",
        title="Present",
        album_artist_id=None,
        album_id=None,
        album_position=2,
        year="2019",
        plays_count=0,
        cover=bytes(),
        cover_type="",
        bit_rate=10,
        bits_per_sample=10,
        sample_rate=10,
        channels=10,
        duration=10,
    )

    track_flac = db.Track(
        file_path=TEST_FLAC_FILE,
        file_size=3,
        type="audio/flac",
        title="Already",
        album_artist_id=None,
        album_id=None,
        album_position=1,
        year="2020",
        plays_count=0,
        cover=bytes(),
        cover_type="",
        bit_rate=10,
        bits_per_sample=10,
        sample_rate=10,
        channels=10,
        duration=10,
    )

    new_audio_mp3, _ = utils.update_tags(track_mp3, new_tags)
    new_audio_flac, _ = utils.update_tags(track_flac, new_tags)

    assert str(new_audio_mp3["TIT2"]) == exp_title
    assert new_audio_flac["TITLE"][0] == exp_title

    assert (
        re.split(utils.TAG_MULTIPLE_PATTERN, str(new_audio_mp3["TPE1"])) == exp_artists
    )
    assert new_audio_flac["ARTIST"] == exp_artists

    assert (
        "TPE2" not in new_audio_mp3.tags
        and exp_album_artist is None
        or str(new_audio_mp3["TPE2"]) == exp_album_artist
    )
    assert (
        "ALBUMARTIST" not in new_audio_flac.tags
        and exp_album_artist is None
        or new_audio_flac["ALBUMARTIST"][0] == exp_album_artist
    )

    assert str(new_audio_mp3["TALB"]) == exp_album
    assert new_audio_flac["ALBUM"][0] == exp_album

    assert (
        "TCON" not in new_audio_mp3.tags
        and exp_genres == []
        or re.split(utils.TAG_MULTIPLE_PATTERN, str(new_audio_mp3["TCON"]))
        == exp_genres
    )
    assert (
        "GENRE" not in new_audio_flac.tags
        and exp_genres == []
        or new_audio_flac["GENRE"] == exp_genres
    )

    assert (
        "TRCK" not in new_audio_mp3.tags
        and exp_track_number is None
        or int(str(new_audio_mp3["TRCK"])) == exp_track_number
    )
    assert (
        "TRACKNUMBER" not in new_audio_flac.tags
        and exp_track_number is None
        or int(new_audio_flac["TRACKNUMBER"][0]) == exp_track_number
    )

    assert (
        "TDRC" not in new_audio_mp3.tags
        and exp_year is None
        or str(new_audio_mp3["TDRC"][0]) == exp_year
    )
    assert (
        "DATE" not in new_audio_flac.tags
        and exp_year is None
        or new_audio_flac["DATE"][0] == exp_year
    )

    assert set(utils.get_custom_tags_mp3(new_audio_mp3)) == set(exp_custom)
    assert set(utils.get_custom_tags_flac(new_audio_flac)) == set(exp_custom)
