import pytest
from fastapi.testclient import TestClient
from functools import partial
from sqlalchemy import Engine, create_engine
from sqlmodel import Session, select
from unittest.mock import MagicMock, patch

from src.app import database as db
from src.app.db_loading import AudioInfo, load_audio_data
from src.app.app import app

from tests.integration.fixtures import session, db_uri
from src.app.service_layer import create_user


def get_session_gen(db_uri: str):
    engine = create_engine(db_uri)
    session = Session(engine)
    try:
        yield session
    finally:
        session.connection().close()
        engine.dispose()


def get_default_audio_info() -> AudioInfo:
    audio_info = None
    with patch("os.path.getsize") as mock_getsize:
        mock_getsize.return_value = 1984500
        audio_info = AudioInfo("tracks/t1.mp3")
    audio_info.type = "audio/mpeg"
    audio_info.title = "track1"
    audio_info.artists = ["ar1", "ar2"]
    audio_info.album_artist = "ar1"
    audio_info.album = "al1"
    audio_info.genres = ["g1", "g2"]
    audio_info.track_number = 1
    audio_info.year = 2020
    audio_info.cover = bytes()
    audio_info.cover_type = ""
    audio_info.custom_tags = []
    audio_info.bit_rate = 128 * 1024
    audio_info.bits_per_sample = 3
    audio_info.sample_rate = 44100
    audio_info.channels = 2
    audio_info.duration = 60

    return audio_info


def test_get_existing_song(db_uri: str):
    session_gen = partial(get_session_gen, db_uri=db_uri)

    audio_info = get_default_audio_info()

    g = session_gen()
    session = next(g)
    create_user(session, "admin", "admin")
    load_audio_data(audio_info, session)
    g.close()

    app.dependency_overrides[db.get_session] = session_gen
    client = TestClient(app)

    response = client.get("/rest/getSong?id=1&u=admin&p=admin")
    assert response.status_code == 200

    data = response.json()
    subsonic_response = data["subsonic-response"]
    song = subsonic_response["song"]

    assert song["id"] == "1"
    assert song["parent"] == "1"
    assert song["isDir"] == False
    assert song["title"] == "track1"
    assert song["album"] == "al1"
    assert song["artist"] == "ar1, ar2"
    assert song["track"] == 1
    assert song["year"] == 2020
    assert song["genre"] == "g1, g2"
    assert song["coverArt"] == "mf-1"
    assert song["size"] == 1984500
    assert song["contentType"] == "audio/mpeg"
    assert song["suffix"] == ".mp3"
    assert song["duration"] == 60
    assert song["bitRate"] == 128
    assert song["bitDepth"] == 3
    assert song["samplingRate"] == 44100
    assert song["channelCount"] == 2
    assert song["path"] == "tracks/t1.mp3"
    assert song["playCount"] == 0
    assert song["albumId"] == "1"
    assert song["artistId"] == "1"
    assert song["type"] == "music"

    genres = song["genres"]
    genre0 = genres[0]
    assert genre0["name"] == "g1"
    genre1 = genres[1]
    assert genre1["name"] == "g2"

    artists = song["artists"]
    artist0 = artists[0]
    assert artist0["id"] == "1"
    assert artist0["name"] == "ar1"
    artist1 = artists[1]
    assert artist1["id"] == "2"
    assert artist1["name"] == "ar2"


def test_get_nonexistent_song(db_uri: str):
    session_gen = partial(get_session_gen, db_uri=db_uri)
    
    g = session_gen()
    session = next(g)
    create_user(session, "admin", "admin")
    g.close()

    app.dependency_overrides[db.get_session] = session_gen
    client = TestClient(app)

    response = client.get("/rest/getSong?id=2&u=admin&p=admin")
    
    assert response.status_code == 404 
    
    data = response.json()
    assert data["detail"] == "No such id"


@pytest.mark.parametrize(
    "id, status_code",
    [
        (1, 200),
        (2, 404),
    ],
)
@patch("os.path.getsize")
def test_get_album(
    mock_getsize: MagicMock, session: Session, id: int, status_code: int
):
    mock_getsize.return_value = 1

    audio_info = AudioInfo("tracks/t1.mp3")
    audio_info.type = "audio/mpeg"
    audio_info.title = "track1"
    audio_info.artists = ["ar1", "ar2"]
    audio_info.album_artist = "ar1"
    audio_info.album = "al1"
    audio_info.genres = ["g1", "g2"]
    audio_info.track_number = 1
    audio_info.year = 2020
    audio_info.cover = bytes()
    audio_info.cover_type = ""
    audio_info.custom_tags = []
    audio_info.bit_rate = 1
    audio_info.bits_per_sample = 1
    audio_info.sample_rate = 1
    audio_info.channels = 1
    audio_info.duration = 1

    load_audio_data(audio_info, session)

    audio_info = AudioInfo("tracks/t2.mp3")
    audio_info.type = "audio/mpeg"
    audio_info.title = "track2"
    audio_info.artists = ["ar1", "ar2"]
    audio_info.album_artist = "ar1"
    audio_info.album = "al1"
    audio_info.genres = ["g1", "g2"]
    audio_info.track_number = 2
    audio_info.year = 2021
    audio_info.cover = bytes()
    audio_info.cover_type = ""
    audio_info.custom_tags = []
    audio_info.bit_rate = 1
    audio_info.bits_per_sample = 1
    audio_info.sample_rate = 1
    audio_info.channels = 1
    audio_info.duration = 1

    load_audio_data(audio_info, session)

    album = session.exec(select(db.Album).where(db.Album.name == "al1")).one()

    assert album.total_tracks == 2


@pytest.mark.parametrize(
    "id, status_code",
    [
        (1, 200),
        (2, 404),
    ],
)
@patch("os.path.getsize")
def test_get_artist(
    mock_getsize: MagicMock, session: Session, id: int, status_code: int
):
    mock_getsize.return_value = 1

    audio_info = AudioInfo("tracks/t1.mp3")
    audio_info.type = "audio/mpeg"
    audio_info.title = "track1"
    audio_info.artists = ["ar1", "ar2"]
    audio_info.album_artist = "ar1"
    audio_info.album = "al1"
    audio_info.genres = ["g1", "g2"]
    audio_info.track_number = 1
    audio_info.year = 2020
    audio_info.cover = bytes()
    audio_info.cover_type = ""
    audio_info.custom_tags = []
    audio_info.bit_rate = 1
    audio_info.bits_per_sample = 1
    audio_info.sample_rate = 1
    audio_info.channels = 1
    audio_info.duration = 1

    load_audio_data(audio_info, session)

    audio_info = AudioInfo("tracks/t2.mp3")
    audio_info.type = "audio/mpeg"
    audio_info.title = "track2"
    audio_info.artists = ["ar1", "ar2"]
    audio_info.album_artist = "ar1"
    audio_info.album = "al2"
    audio_info.genres = ["g1", "g2"]
    audio_info.track_number = 2
    audio_info.year = 2021
    audio_info.cover = bytes()
    audio_info.cover_type = ""
    audio_info.custom_tags = []
    audio_info.bit_rate = 1
    audio_info.bits_per_sample = 1
    audio_info.sample_rate = 1
    audio_info.channels = 1
    audio_info.duration = 1

    load_audio_data(audio_info, session)

    artist = session.exec(select(db.Artist).where(db.Artist.name == "ar1")).one()

    assert len(artist.albums) == 2


@patch("os.path.getsize")
def test_get_artists(mock_getsize: MagicMock, session: Session):
    mock_getsize.return_value = 1

    audio_info = AudioInfo("tracks/t1.mp3")
    audio_info.type = "audio/mpeg"
    audio_info.title = "track1"
    audio_info.artists = ["ar1", "ar2"]
    audio_info.album_artist = "ar1"
    audio_info.album = "al1"
    audio_info.genres = ["g1", "g2"]
    audio_info.track_number = 1
    audio_info.year = 2020
    audio_info.cover = bytes()
    audio_info.cover_type = ""
    audio_info.custom_tags = []
    audio_info.bit_rate = 1
    audio_info.bits_per_sample = 1
    audio_info.sample_rate = 1
    audio_info.channels = 1
    audio_info.duration = 1

    load_audio_data(audio_info, session)

    audio_info = AudioInfo("tracks/t2.mp3")
    audio_info.type = "audio/mpeg"
    audio_info.title = "track2"
    audio_info.artists = ["ar1", "ar2"]
    audio_info.album_artist = "ar1"
    audio_info.album = "al2"
    audio_info.genres = ["g1", "g2"]
    audio_info.track_number = 2
    audio_info.year = 2021
    audio_info.cover = bytes()
    audio_info.cover_type = ""
    audio_info.custom_tags = []
    audio_info.bit_rate = 1
    audio_info.bits_per_sample = 1
    audio_info.sample_rate = 1
    audio_info.channels = 1
    audio_info.duration = 1

    load_audio_data(audio_info, session)

    artists = session.exec(select(db.Artist)).all()

    assert len(artists) == 2


@patch("os.path.getsize")
def test_get_albums(mock_getsize: MagicMock, session: Session):
    mock_getsize.return_value = 1

    audio_info = AudioInfo("tracks/t1.mp3")
    audio_info.type = "audio/mpeg"
    audio_info.title = "track1"
    audio_info.artists = ["ar1", "ar2"]
    audio_info.album_artist = "ar1"
    audio_info.album = "al1"
    audio_info.genres = ["g1", "g2"]
    audio_info.track_number = 1
    audio_info.year = 2020
    audio_info.cover = bytes()
    audio_info.cover_type = ""
    audio_info.custom_tags = []
    audio_info.bit_rate = 1
    audio_info.bits_per_sample = 1
    audio_info.sample_rate = 1
    audio_info.channels = 1
    audio_info.duration = 1

    load_audio_data(audio_info, session)

    audio_info = AudioInfo("tracks/t2.mp3")
    audio_info.type = "audio/mpeg"
    audio_info.title = "track2"
    audio_info.artists = ["ar1", "ar2"]
    audio_info.album_artist = "ar1"
    audio_info.album = "al2"
    audio_info.genres = ["g1", "g2"]
    audio_info.track_number = 2
    audio_info.year = 2021
    audio_info.cover = bytes()
    audio_info.cover_type = ""
    audio_info.custom_tags = []
    audio_info.bit_rate = 1
    audio_info.bits_per_sample = 1
    audio_info.sample_rate = 1
    audio_info.channels = 1
    audio_info.duration = 1

    load_audio_data(audio_info, session)

    albums = session.exec(select(db.Album)).all()

    assert len(albums) == 2


@patch("os.path.getsize")
def test_search(mock_getsize: MagicMock, session: Session):
    mock_getsize.return_value = 1

    audio_info = AudioInfo("tracks/t1.mp3")
    audio_info.type = "audio/mpeg"
    audio_info.title = "track1"
    audio_info.artists = ["ar1", "ar2"]
    audio_info.album_artist = "ar1"
    audio_info.album = "al1"
    audio_info.genres = ["g1", "g2"]
    audio_info.track_number = 1
    audio_info.year = 2020
    audio_info.cover = bytes()
    audio_info.cover_type = ""
    audio_info.custom_tags = []
    audio_info.bit_rate = 1
    audio_info.bits_per_sample = 1
    audio_info.sample_rate = 1
    audio_info.channels = 1
    audio_info.duration = 1

    load_audio_data(audio_info, session)

    audio_info = AudioInfo("tracks/t2.mp3")
    audio_info.type = "audio/mpeg"
    audio_info.title = "track2"
    audio_info.artists = ["ar1", "ar2"]
    audio_info.album_artist = "ar1"
    audio_info.album = "al2"
    audio_info.genres = ["g1", "g2"]
    audio_info.track_number = 2
    audio_info.year = 2021
    audio_info.cover = bytes()
    audio_info.cover_type = ""
    audio_info.custom_tags = []
    audio_info.bit_rate = 1
    audio_info.bits_per_sample = 1
    audio_info.sample_rate = 1
    audio_info.channels = 1
    audio_info.duration = 1

    load_audio_data(audio_info, session)

    tracks = session.exec(select(db.Track)).all()
    albums = session.exec(select(db.Album)).all()
    artists = session.exec(select(db.Artist)).all()

    assert len(tracks) == 2
    assert len(albums) == 2
    assert len(artists) == 2


@patch("os.path.getsize")
def test_get_genres(mock_getsize: MagicMock, session: Session):
    mock_getsize.return_value = 1

    audio_info = AudioInfo("tracks/t1.mp3")
    audio_info.type = "audio/mpeg"
    audio_info.title = "track1"
    audio_info.artists = ["ar1", "ar2"]
    audio_info.album_artist = "ar1"
    audio_info.album = "al1"
    audio_info.genres = ["g1", "g2"]
    audio_info.track_number = 1
    audio_info.year = 2020
    audio_info.cover = bytes()
    audio_info.cover_type = ""
    audio_info.custom_tags = []
    audio_info.bit_rate = 1
    audio_info.bits_per_sample = 1
    audio_info.sample_rate = 1
    audio_info.channels = 1
    audio_info.duration = 1

    load_audio_data(audio_info, session)

    audio_info = AudioInfo("tracks/t2.mp3")
    audio_info.type = "audio/mpeg"
    audio_info.title = "track2"
    audio_info.artists = ["ar1", "ar2"]
    audio_info.album_artist = "ar1"
    audio_info.album = "al2"
    audio_info.genres = ["g1", "g2"]
    audio_info.track_number = 2
    audio_info.year = 2021
    audio_info.cover = bytes()
    audio_info.cover_type = ""
    audio_info.custom_tags = []
    audio_info.bit_rate = 1
    audio_info.bits_per_sample = 1
    audio_info.sample_rate = 1
    audio_info.channels = 1
    audio_info.duration = 1

    load_audio_data(audio_info, session)

    genres = session.exec(select(db.Genre)).all()

    assert len(genres) == 2


@patch("os.path.getsize")
def test_get_tracks_by_genre(mock_getsize: MagicMock, session: Session):
    mock_getsize.return_value = 1

    audio_info = AudioInfo("tracks/t1.mp3")
    audio_info.type = "audio/mpeg"
    audio_info.title = "track1"
    audio_info.artists = ["ar1", "ar2"]
    audio_info.album_artist = "ar1"
    audio_info.album = "al1"
    audio_info.genres = ["g1", "g2"]
    audio_info.track_number = 1
    audio_info.year = 2020
    audio_info.cover = bytes()
    audio_info.cover_type = ""
    audio_info.custom_tags = []
    audio_info.bit_rate = 1
    audio_info.bits_per_sample = 1
    audio_info.sample_rate = 1
    audio_info.channels = 1
    audio_info.duration = 1

    load_audio_data(audio_info, session)

    audio_info = AudioInfo("tracks/t2.mp3")
    audio_info.type = "audio/mpeg"
    audio_info.title = "track2"
    audio_info.artists = ["ar1", "ar2"]
    audio_info.album_artist = "ar1"
    audio_info.album = "al2"
    audio_info.genres = ["g1", "g2"]
    audio_info.track_number = 2
    audio_info.year = 2021
    audio_info.cover = bytes()
    audio_info.cover_type = ""
    audio_info.custom_tags = []
    audio_info.bit_rate = 1
    audio_info.bits_per_sample = 1
    audio_info.sample_rate = 1
    audio_info.channels = 1
    audio_info.duration = 1

    load_audio_data(audio_info, session)

    tracks = session.exec(select(db.Track)).all()
    genres = session.exec(select(db.Genre)).all()

    assert len(tracks) == 2
    assert len(genres) == 2


@patch("os.path.getsize")
def test_star(mock_getsize: MagicMock, session: Session):
    mock_getsize.return_value = 1

    session.add(db.User(login="test_user", password="password", avatar="line"))
    session.commit()

    audio_info = AudioInfo("tracks/t1.mp3")
    audio_info.type = "audio/mpeg"
    audio_info.title = "track1"
    audio_info.artists = ["ar1", "ar2"]
    audio_info.album_artist = "ar1"
    audio_info.album = "al1"
    audio_info.genres = ["g1", "g2"]
    audio_info.track_number = 1
    audio_info.year = 2020
    audio_info.cover = bytes()
    audio_info.cover_type = ""
    audio_info.custom_tags = []
    audio_info.bit_rate = 1
    audio_info.bits_per_sample = 1
    audio_info.sample_rate = 1
    audio_info.channels = 1
    audio_info.duration = 1

    load_audio_data(audio_info, session)

    audio_info = AudioInfo("tracks/t2.mp3")
    audio_info.type = "audio/mpeg"
    audio_info.title = "track2"
    audio_info.artists = ["ar1", "ar2"]
    audio_info.album_artist = "ar1"
    audio_info.album = "al2"
    audio_info.genres = ["g1", "g2"]
    audio_info.track_number = 2
    audio_info.year = 2021
    audio_info.cover = bytes()
    audio_info.cover_type = ""
    audio_info.custom_tags = []
    audio_info.bit_rate = 1
    audio_info.bits_per_sample = 1
    audio_info.sample_rate = 1
    audio_info.channels = 1
    audio_info.duration = 1

    load_audio_data(audio_info, session)

    tracks = session.exec(select(db.Track)).all()
    albums = session.exec(select(db.Album)).all()
    artists = session.exec(select(db.Artist)).all()

    assert len(tracks) == 2
    assert len(albums) == 2
    assert len(artists) == 2


@patch("os.path.getsize")
def test_unstar(mock_getsize: MagicMock, session: Session):
    mock_getsize.return_value = 1

    session.add(db.User(login="test_user", password="password", avatar="line"))
    session.commit()

    audio_info = AudioInfo("tracks/t1.mp3")
    audio_info.type = "audio/mpeg"
    audio_info.title = "track1"
    audio_info.artists = ["ar1", "ar2"]
    audio_info.album_artist = "ar1"
    audio_info.album = "al1"
    audio_info.genres = ["g1", "g2"]
    audio_info.track_number = 1
    audio_info.year = 2020
    audio_info.cover = bytes()
    audio_info.cover_type = ""
    audio_info.custom_tags = []
    audio_info.bit_rate = 1
    audio_info.bits_per_sample = 1
    audio_info.sample_rate = 1
    audio_info.channels = 1
    audio_info.duration = 1

    load_audio_data(audio_info, session)

    audio_info = AudioInfo("tracks/t2.mp3")
    audio_info.type = "audio/mpeg"
    audio_info.title = "track2"
    audio_info.artists = ["ar1", "ar2"]
    audio_info.album_artist = "ar1"
    audio_info.album = "al2"
    audio_info.genres = ["g1", "g2"]
    audio_info.track_number = 2
    audio_info.year = 2021
    audio_info.cover = bytes()
    audio_info.cover_type = ""
    audio_info.custom_tags = []
    audio_info.bit_rate = 1
    audio_info.bits_per_sample = 1
    audio_info.sample_rate = 1
    audio_info.channels = 1
    audio_info.duration = 1

    load_audio_data(audio_info, session)

    tracks = session.exec(select(db.Track)).all()
    albums = session.exec(select(db.Album)).all()
    artists = session.exec(select(db.Artist)).all()

    assert len(tracks) == 2
    assert len(albums) == 2
    assert len(artists) == 2


@patch("os.path.getsize")
def test_get_starred(mock_getsize: MagicMock, session: Session):
    mock_getsize.return_value = 1

    session.add(db.User(login="test_user", password="password", avatar="line"))
    session.commit()

    audio_info = AudioInfo("tracks/t1.mp3")
    audio_info.type = "audio/mpeg"
    audio_info.title = "track1"
    audio_info.artists = ["ar1", "ar2"]
    audio_info.album_artist = "ar1"
    audio_info.album = "al1"
    audio_info.genres = ["g1", "g2"]
    audio_info.track_number = 1
    audio_info.year = 2020
    audio_info.cover = bytes()
    audio_info.cover_type = ""
    audio_info.custom_tags = []
    audio_info.bit_rate = 1
    audio_info.bits_per_sample = 1
    audio_info.sample_rate = 1
    audio_info.channels = 1
    audio_info.duration = 1

    load_audio_data(audio_info, session)

    audio_info = AudioInfo("tracks/t2.mp3")
    audio_info.type = "audio/mpeg"
    audio_info.title = "track2"
    audio_info.artists = ["ar1", "ar2"]
    audio_info.album_artist = "ar1"
    audio_info.album = "al2"
    audio_info.genres = ["g1", "g2"]
    audio_info.track_number = 2
    audio_info.year = 2021
    audio_info.cover = bytes()
    audio_info.cover_type = ""
    audio_info.custom_tags = []
    audio_info.bit_rate = 1
    audio_info.bits_per_sample = 1
    audio_info.sample_rate = 1
    audio_info.channels = 1
    audio_info.duration = 1

    load_audio_data(audio_info, session)

    tracks = session.exec(select(db.Track)).all()
    albums = session.exec(select(db.Album)).all()
    artists = session.exec(select(db.Artist)).all()

    assert len(tracks) == 2
    assert len(albums) == 2
    assert len(artists) == 2
