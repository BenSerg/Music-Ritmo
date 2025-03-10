import pytest
import re
from PIL import Image
from typing import Any
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.id3 import TXXX

from src.app import utils
from src.app import database as db

TEST_MP3_FILE = "tracks/MACAN_-_I_AM_78125758.mp3"
TEST_FLAC_FILE = "tracks/Atomic Heart/03. Arlekino (Geoffrey Day Remix).flac"


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
        cover = Image.open(utils.DEFAULT_COVER_PATH)
        cover.thumbnail(size)
        preview_bytes, format = utils.get_cover_preview(utils.image_to_bytes(cover))
        preview_image = utils.bytes_to_image(preview_bytes)
        width, height = preview_image.size

        assert (
            width <= utils.MAX_COVER_PREVIEW_SIZE
            and height <= utils.MAX_COVER_PREVIEW_SIZE
        )
        assert format == str(cover_preview.format).lower()


@pytest.mark.parametrize("audio_type", ["audio/mpeg", "audio/flac"])
@pytest.mark.parametrize(
    "tag_name_mp3, tag_name_flac",
    [
        ("TPE2", "ALBUMARTIST"),
        ("TRCK", "TRACKNUMBER"),
        ("TDRC", "DATE"),
        ("TCON", "GENRE"),
    ],
)
def test_pop_tag(audio_type: str, tag_name_mp3: str, tag_name_flac: str):
    tag_names = {utils.AudioType.MP3: tag_name_mp3, utils.AudioType.FLAC: tag_name_flac}

    match audio_type:
        case "audio/mpeg":
            audio = MP3(TEST_MP3_FILE)
            audio_type_value = utils.AudioType.MP3
        case "audio/flac":
            audio = FLAC(TEST_FLAC_FILE)
            audio_type_value = utils.AudioType.FLAC

    utils.popTag(audio, audio_type_value, tag_names)

    assert tag_names[audio_type_value] not in audio


@pytest.mark.parametrize("audio_type", ["audio/mpeg", "audio/flac"])
@pytest.mark.parametrize(
    "custom_tags",
    [
        [],
        [("custom1", "value1")],
        [
            ("custom1", "value1"),
            ("custom2", "value2"),
            ("custom3", "value3"),
            ("custom4", "value1"),
        ],
        [("новыйтег1", "значение1")],
        [
            ("новыйтег1", "значение1"),
            ("новый тег1", "значение1"),
        ],
    ],
)
def test_get_custom_tags(audio_type: str, custom_tags: list[tuple[str, str]]):
    match audio_type:
        case "audio/mpeg":
            audio = MP3(TEST_MP3_FILE)
        case "audio/flac":
            audio = FLAC(TEST_FLAC_FILE)

    for tag in audio.tags:
        if str(tag).startswith("TXXX:"):
            audio.pop(tag)

    for key, value in custom_tags:
        match audio_type:
            case "audio/mpeg":
                audio["TXXX:" + key] = TXXX(desc=key, text=value)  # type: ignore[no-untyped-call]
            case "audio/flac":
                audio["TXXX:" + str(hash(key))] = key + "; " + value

    assert set(utils.get_custom_tags(audio)) == set(custom_tags)


@pytest.mark.parametrize("audio_type", ["audio/mpeg", "audio/flac"])
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
                "artists": "present_artist1; new artist1, new artist2",
                "album_artist": None,
                "album": "present_album1",
                "genres": "present_genre1; new genre1, new genre2",
                "album_position": "2",
                "year": "2020",
                "new custom1": "new value1",
                "present_custom1": "present_value1",
            },
            (
                "Present",
                ["present_artist1", "new artist1", "new artist2"],
                None,
                "present_album1",
                ["present_genre1", "new genre1", "new genre2"],
                2,
                "2020",
                [("present_custom1", "present_value1"), ("new custom1", "new value1")],
            ),
        ),
        (
            {
                "title": "Название",
                "artists": "present_artist1, артист1",
                "album_artist": None,
                "album": "альбом1",
                "genres": "present_genre1; жанр1",
                "album_position": "0",
                "year": "2021",
                "новый_тег": "значение",
            },
            (
                "Название",
                ["present_artist1", "артист1"],
                None,
                "альбом1",
                ["present_genre1", "жанр1"],
                0,
                "2021",
                [("новый_тег", "значение")],
            ),
        ),
        (
            {
                "title": "Название",
                "artists": "present_artist1, артист 1",
                "album_artist": None,
                "album": "альбом1",
                "genres": "present_genre1; жанр 1",
                "album_position": "0",
                "year": "2021",
                "новый_тег1": "значение 1",
                "новый тег2": "значение 2",
                "новый/тег3": "значение 3",
            },
            (
                "Название",
                ["present_artist1", "артист 1"],
                None,
                "альбом1",
                ["present_genre1", "жанр 1"],
                0,
                "2021",
                [
                    ("новый_тег1", "значение 1"),
                    ("новый тег2", "значение 2"),
                    ("новый/тег3", "значение 3"),
                ],
            ),
        ),
    ],
)
def test_update_tags(audio_type: str, new_tags: dict[str, Any], expected_tags):
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

    match audio_type:
        case "audio/mpeg":
            track = db.Track(
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
        case "audio/flac":
            track = db.Track(
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

    updated_audio, _ = utils.update_tags(track, new_tags)

    match audio_type:
        case "audio/mpeg":
            assert str(updated_audio["TIT2"]) == exp_title
            assert (
                re.split(utils.TAG_MULTIPLE_PATTERN, str(updated_audio["TPE1"]))
                == exp_artists
            )
            assert (
                "TPE2" not in updated_audio.tags
                and exp_album_artist is None
                or str(updated_audio["TPE2"]) == exp_album_artist
            )
            assert str(updated_audio["TALB"]) == exp_album
            assert (
                "TCON" not in updated_audio.tags
                and exp_genres == []
                or re.split(utils.TAG_MULTIPLE_PATTERN, str(updated_audio["TCON"]))
                == exp_genres
            )
            assert (
                "TRCK" not in updated_audio.tags
                and exp_track_number is None
                or int(str(updated_audio["TRCK"])) == exp_track_number
            )
            assert (
                "TDRC" not in updated_audio.tags
                and exp_year is None
                or str(updated_audio["TDRC"][0]) == exp_year
            )

        case "audio/flac":
            assert updated_audio["TITLE"][0] == exp_title
            assert updated_audio["ARTIST"] == exp_artists
            assert (
                "ALBUMARTIST" not in updated_audio.tags
                and exp_album_artist is None
                or updated_audio["ALBUMARTIST"][0] == exp_album_artist
            )
            assert updated_audio["ALBUM"][0] == exp_album
            assert (
                "GENRE" not in updated_audio.tags
                and exp_genres == []
                or updated_audio["GENRE"] == exp_genres
            )
            assert (
                "TRACKNUMBER" not in updated_audio.tags
                and exp_track_number is None
                or int(updated_audio["TRACKNUMBER"][0]) == exp_track_number
            )
            assert (
                "DATE" not in updated_audio.tags
                and exp_year is None
                or updated_audio["DATE"][0] == exp_year
            )

    assert set(utils.get_custom_tags(updated_audio)) == set(exp_custom)
