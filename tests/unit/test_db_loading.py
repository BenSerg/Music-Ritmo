import pytest
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.id3 import TIT2, TPE1, TPE2, TALB, TCON, TRCK, TDRC  # type: ignore[attr-defined]

# from unittest.mock import MagicMock, patch
# from sqlmodel import SQLModel, create_engine, Session, select

from src.app import db_loading

# from src.app import database as db

TEST_MP3_FILE = "tracks/MACAN_-_I_AM_78125758.mp3"
TEST_FLAC_FILE = "tracks/Atomic Heart/03. Arlekino (Geoffrey Day Remix).flac"


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
                "0",
                "2020",
            ),
            (
                "title",
                ["artist1", "artist2"],
                "artist3",
                "album",
                ["genre1", "genre2"],
                0,
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
        (
            "трек",
            (
                "название",
                "артист1, артист2, artist1",
                "артист2",
                "альбом",
                "поп, рок, jazz",
                "1",
                "2021",
            ),
            (
                "название",
                ["артист1", "артист2", "artist1"],
                "артист2",
                "альбом",
                ["поп", "рок", "jazz"],
                1,
                "2021",
            ),
        ),
    ],
)
def test_extract_metadata_mp3(file_name: str, file_tags, expected_tags):
    (
        exp_title,
        exp_artists,
        exp_album_artist,
        exp_album,
        exp_genres,
        exp_track_number,
        exp_year,
    ) = expected_tags

    audio_info = db_loading.AudioInfo(TEST_MP3_FILE)
    audio = MP3(TEST_MP3_FILE)

    tag_names = [
        "TIT2",
        "TPE1",
        "TPE2",
        "TALB",
        "TCON",
        "TRCK",
        "TDRC",
    ]

    audio_info.file_path = file_name
    for name, value in zip(tag_names, file_tags):
        if value is not None:
            audio[name] = eval(name)(text=[value])  # type: ignore[no-untyped-call]
        elif name in audio.tags:
            audio.pop(name)

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
        (
            "трек",
            (
                "название",
                ["артист 1", "артист 2", "artist1"],
                "артист 2",
                "альбом",
                ["поп", "рок", "jazz"],
                "1",
                "2021",
            ),
            (
                "название",
                ["артист 1", "артист 2", "artist1"],
                "артист 2",
                "альбом",
                ["поп", "рок", "jazz"],
                1,
                "2021",
            ),
        ),
    ],
)
def test_extract_metadata_flac(
    file_name: str,
    file_tags,
    expected_tags,
):
    (
        exp_title,
        exp_artists,
        exp_album_artist,
        exp_album,
        exp_genres,
        exp_track_number,
        exp_year,
    ) = expected_tags

    audio_info = db_loading.AudioInfo(TEST_FLAC_FILE)
    audio = FLAC(TEST_FLAC_FILE)

    tag_names = [
        "TITLE",
        "ARTIST",
        "ALBUMARTIST",
        "ALBUM",
        "GENRE",
        "TRACKNUMBER",
        "DATE",
    ]

    audio_info.file_path = file_name
    for name, value in zip(tag_names, file_tags):
        if value is not None:
            audio[name] = value
        elif name in audio.tags:
            audio.pop(name)

    db_loading.extract_metadata_flac(audio, audio_info)

    assert audio_info.title == exp_title
    assert audio_info.artists == exp_artists
    assert audio_info.album_artist == exp_album_artist
    assert audio_info.album == exp_album
    assert audio_info.genres == exp_genres
    assert audio_info.track_number == exp_track_number
    assert audio_info.year == exp_year


# @pytest.fixture
# def session():
#     engine = create_engine("sqlite:///:memory:")
#     SQLModel.metadata.create_all(engine)

#     session = Session(engine, autoflush=False)

#     temp_artist = db.Artist(name="present_artist1")
#     temp_album = db.Album(
#         name="present_album1",
#         album_artist_id=None,
#         total_tracks=1,
#         year="2019",
#         cover=bytes(),
#         artists=[temp_artist],
#     )
#     session.add(temp_album)
#     session.commit()
#     session.refresh(temp_artist)
#     session.refresh(temp_album)

#     temp_genre = db.Genre(name="present_genre1")
#     temp_custom_tag = db.CustomTag(
#         name="present_custom1", value="present_value1", updated=False
#     )

#     temp_track_mp3 = db.Track(
#         file_path="./present_track.mp3",
#         file_size=3,
#         type="audio/mpeg",
#         title="Present",
#         album_artist_id=None,
#         album_id=temp_album.id,
#         album_position=2,
#         year="2019",
#         plays_count=0,
#         cover=bytes(),
#         cover_type="",
#         bit_rate=10,
#         bits_per_sample=10,
#         sample_rate=10,
#         channels=10,
#         duration=10,
#         artists=[temp_artist],
#         genres=[temp_genre],
#         custom_tags=[temp_custom_tag],
#     )
#     session.add(temp_track_mp3)

#     temp_track_flac = db.Track(
#         file_path="./already_song.flac",
#         file_size=3,
#         type="audio/flac",
#         title="Already",
#         album_artist_id=None,
#         album_id=temp_album.id,
#         album_position=1,
#         year="2020",
#         plays_count=0,
#         cover=bytes(),
#         cover_type="",
#         bit_rate=10,
#         bits_per_sample=10,
#         sample_rate=10,
#         channels=10,
#         duration=10,
#         artists=[temp_artist],
#         genres=[temp_genre],
#         custom_tags=[temp_custom_tag],
#     )
#     session.add(temp_track_flac)
#     session.commit()

#     try:
#         yield session
#     finally:
#         session.close()
#         SQLModel.metadata.drop_all(engine)


# @pytest.mark.parametrize(
#     "file_path, type, title, artists, album_artist, album, genres, track_number, year, custom_tags",
#     [
#         (
#             "./newaudio",
#             "audio/mpeg",
#             "newaudio",
#             ["Неизвестный исполнитель"],
#             None,
#             "Неизвестный альбом",
#             [],
#             None,
#             None,
#             [],
#         ),
#         (
#             "./newaudio",
#             "audio/flac",
#             "title",
#             ["artist1"],
#             "artist1",
#             "album",
#             ["genre1"],
#             1,
#             "2020",
#             [("custom1", "value1")],
#         ),
#         (
#             "./newaudio",
#             "audio/flac",
#             "title",
#             ["artist1", "artist2"],
#             "artist2",
#             "album",
#             ["genre1", "genre2"],
#             10,
#             "2020-2021",
#             [("custom1", "value1"), ("custom2", "value2")],
#         ),
#         (
#             "./present_track.mp3",
#             "audio/mpeg",
#             "present_track",
#             ["Неизвестный исполнитель"],
#             None,
#             "Неизвестный альбом",
#             [],
#             None,
#             None,
#             [],
#         ),
#         (
#             "./present_track.mp3",
#             "audio/mpeg",
#             "Present",
#             ["present_artist1"],
#             "present_artist1",
#             "present_album",
#             ["present_genre1"],
#             10,
#             "2019",
#             [("present_custom1", "present_value1")],
#         ),
#         (
#             "./present_track.mp3",
#             "audio/mpeg",
#             "Present",
#             ["present_artist1", "artist2"],
#             "artist2",
#             "album",
#             ["present_genre1", "genre2"],
#             5,
#             "2020-2021",
#             [("present_custom1", "present_value1"), ("custom2", "value2")],
#         ),
#     ],
# )
# @patch("os.path.getsize")
# def test_db_load_audio(
#     mock_getsize: MagicMock,
#     session: Session,
#     file_path: str,
#     type: str,
#     title: str,
#     artists: list[str],
#     album_artist: str | None,
#     album: str,
#     genres: list[str],
#     track_number: int | None,
#     year: str | None,
#     custom_tags: list[tuple[str, str]],
# ):
#     mock_getsize.return_value = 1

#     audio_info = db_loading.AudioInfo("temp")
#     audio_info.file_path = file_path
#     audio_info.type = type
#     audio_info.title = title
#     audio_info.artists = artists
#     audio_info.album_artist = album_artist
#     audio_info.album = album
#     audio_info.genres = genres
#     audio_info.track_number = track_number
#     audio_info.year = year
#     audio_info.cover = bytes()
#     audio_info.cover_type = ""
#     audio_info.custom_tags = custom_tags
#     audio_info.bit_rate = 1
#     audio_info.bits_per_sample = 1
#     audio_info.sample_rate = 1
#     audio_info.channels = 1
#     audio_info.duration = 1

#     db_loading.load_audio_data(audio_info, session)

#     track = session.exec(select(db.Track).where(db.Track.file_path == file_path)).one()

#     assert track.file_path == file_path
#     assert track.type == type
#     assert track.title == title

#     artists_names = list(artist.name for artist in track.artists)
#     for artist in artists:
#         assert artist in artists_names

#     if album_artist is None:
#         assert track.album_artist_id is None
#     else:
#         assert track.album_artist_id is not None
#         album_artist_db = session.exec(
#             select(db.Artist).where(db.Artist.id == track.album_artist_id)
#         ).one()
#         assert album_artist_db.name == album_artist

#     assert track.album.name == album
#     genres_names = list(genre.name for genre in track.genres)
#     for genre in genres:
#         assert genre in genres_names

#     assert track.album_position == track_number
#     assert track.year == year

#     track_custom_tags = list(
#         (custom_tag.name, custom_tag.value) for custom_tag in track.custom_tags
#     )
#     for name, value in custom_tags:
#         assert (name, value) in track_custom_tags
