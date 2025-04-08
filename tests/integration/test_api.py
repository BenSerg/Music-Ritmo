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
from datetime import datetime


def get_session_gen(db_uri: str):
    engine = create_engine(db_uri)
    session = Session(engine)
    try:
        yield session
    finally:
        session.connection().close()
        engine.dispose()


def get_default_audio_info(file_path="tracks/t1.mp3") -> AudioInfo:
    audio_info = None
    with patch("os.path.getsize") as mock_getsize:
        mock_getsize.return_value = 1984500
        audio_info = AudioInfo(file_path)
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


def test_get_album_with_songs(db_uri: str):
    session_gen = partial(get_session_gen, db_uri=db_uri)

    g = session_gen()
    session = next(g)

    create_user(session, "admin", "admin")

    audio1 = get_default_audio_info("tracks/t1.mp3")
    audio1.title = "track1"
    audio1.album = "al1"
    load_audio_data(audio1, session)

    audio2 = get_default_audio_info("tracks/t2.mp3")
    audio2.title = "track2"
    audio2.album = "al1"
    audio2.track_number = 2
    load_audio_data(audio2, session)

    g.close()

    app.dependency_overrides[db.get_session] = session_gen
    client = TestClient(app)

    response = client.get("/rest/getAlbum?id=1&u=admin&p=admin")
    assert response.status_code == 200

    data = response.json()
    subsonic_response = data["subsonic-response"]
    album = subsonic_response["album"]
    assert album["id"] == "1"
    assert album["name"] == "al1"
    assert album["artist"] == "ar1"
    assert album["artistId"] == "1"
    assert album["songCount"] == 2
    assert album["duration"] == 120
    assert album["playCount"] == 0
    assert album["year"] == 2020
    assert album["genre"] == "g1, g2"

    genres = album["genres"]
    assert genres == [{"name": "g1"}, {"name": "g2"}]

    artists = album["artists"]
    assert artists == [{"id": "1", "name": "ar1"}]

    songs = album["song"]
    assert len(songs) == 2

    assert songs[0]["id"] == "1"
    assert songs[0]["title"] == "track1"
    assert songs[0]["track"] == 1

    assert songs[1]["id"] == "2"
    assert songs[1]["title"] == "track2"
    assert songs[1]["track"] == 2


def test_get_nonexistent_album(db_uri: str):
    session_gen = partial(get_session_gen, db_uri=db_uri)

    g = session_gen()
    session = next(g)
    create_user(session, "admin", "admin")
    g.close()

    app.dependency_overrides[db.get_session] = session_gen
    client = TestClient(app)

    response = client.get("/rest/getAlbum?id=2&u=admin&p=admin")

    assert response.status_code == 404

    data = response.json()
    assert data["detail"] == "No such id"


def test_get_existing_artist(db_uri: str):
    session_gen = partial(get_session_gen, db_uri=db_uri)
    g = session_gen()
    session = next(g)

    create_user(session, "admin", "admin")

    audio_info = get_default_audio_info()
    audio_info.title = "track1"
    audio_info.artists = ["ar1"]
    audio_info.album_artist = "ar1"
    audio_info.album = "al1"
    load_audio_data(audio_info, session)
    g.close()

    app.dependency_overrides[db.get_session] = session_gen
    client = TestClient(app)

    response = client.get("/rest/getArtist?id=1&u=admin&p=admin")
    assert response.status_code == 200

    data = response.json()
    subsonic_response = data["subsonic-response"]
    artist = subsonic_response["artist"]
    assert artist["id"] == "1"
    assert artist["name"] == "ar1"
    assert artist["coverArt"] == "ar-1"
    assert artist["albumCount"] == 1
    assert len(artist["album"]) == 1

    album = artist["album"][0]
    assert album["id"] == "1"
    assert album["name"] == "al1"


def test_get_nonexistent_artist(db_uri: str):
    session_gen = partial(get_session_gen, db_uri=db_uri)
    g = session_gen()
    session = next(g)

    create_user(session, "admin", "admin")
    g.close()

    app.dependency_overrides[db.get_session] = session_gen
    client = TestClient(app)

    response = client.get("/rest/getArtist?id=3&u=admin&p=admin")
    assert response.status_code == 404

    data = response.json()
    data = response.json()
    assert data["detail"] == "No such id"


def test_get_artists_with_alphabetical_index(db_uri: str):
    session_gen = partial(get_session_gen, db_uri=db_uri)
    g = session_gen()
    session = next(g)

    create_user(session, "admin", "admin")

    audio1 = get_default_audio_info("tracks/t1.mp3")
    audio1.title = "track1"
    audio1.album = "al1"
    audio1.artists = ["ar1"]
    audio1.album_artist = None
    load_audio_data(audio1, session)

    audio2 = get_default_audio_info("tracks/t2.mp3")
    audio2.title = "track2"
    audio2.album = "al2"
    audio2.artists = ["br2"]
    audio2.album_artist = None
    audio2.track_number = 2
    load_audio_data(audio2, session)
    g.close()

    app.dependency_overrides[db.get_session] = session_gen
    client = TestClient(app)

    response = client.get("/rest/getArtists?u=admin&p=admin")
    assert response.status_code == 200

    data = response.json()
    subsonic_response = data["subsonic-response"]
    artists = subsonic_response["artists"]
    assert artists["ignoredArticles"] == ""

    assert len(artists["index"]) == 2
    assert artists["index"][0]["name"] == "a"
    assert artists["index"][1]["name"] == "b"

    assert len(artists["index"][0]["artist"]) == 1
    assert len(artists["index"][1]["artist"]) == 1

    assert artists["index"][0]["artist"][0]["name"] == "ar1"
    assert artists["index"][1]["artist"][0]["name"] == "br2"


def test_get_album_list_by_play_count(db_uri: str):
    session_gen = partial(get_session_gen, db_uri=db_uri)
    g = session_gen()
    session = next(g)

    create_user(session, "admin", "admin")

    albums_data = [
        {"id": 1, "name": "al1", "play_count": 0},
        {"id": 2, "name": "al2", "play_count": 5},
        {"id": 3, "name": "al3", "play_count": 2},
    ]

    for album_data in albums_data:
        audio_info = get_default_audio_info(f"tracks/t{album_data['id']}.mp3")
        audio_info.title = f"track{album_data['id']}"
        audio_info.album = album_data["name"]
        load_audio_data(audio_info, session)

        album = session.exec(
            select(db.Album).where(db.Album.name == album_data["name"])
        ).one()
        album.play_count = album_data["play_count"]
        session.add(album)

    session.commit()

    g.close()

    app.dependency_overrides[db.get_session] = session_gen
    client = TestClient(app)

    response = client.get("/rest/getAlbumList2?type=frequent&u=admin&p=admin")
    assert response.status_code == 200

    data = response.json()
    album_list = data["subsonic-response"]["albumList2"]
    assert len(album_list["album"]) == 3
    assert album_list["album"][0]["name"] == "al2"
    assert album_list["album"][1]["name"] == "al3"
    assert album_list["album"][2]["name"] == "al1"


def test_get_album_list_alphabetical_by_name(db_uri: str):
    session_gen = partial(get_session_gen, db_uri=db_uri)
    g = session_gen()
    session = next(g)

    create_user(session, "admin", "admin")

    audio1 = get_default_audio_info("tracks/t1.mp3")
    audio1.title = "track1"
    audio1.album = "bl1"
    audio1.artists = ["ar1"]
    load_audio_data(audio1, session)

    audio2 = get_default_audio_info("tracks/t2.mp3")
    audio2.title = "track2"
    audio2.album = "al2"
    audio2.artists = ["ar1"]
    load_audio_data(audio2, session)

    audio3 = get_default_audio_info("tracks/t3.mp3")
    audio3.title = "track3"
    audio3.album = "al3"
    audio3.artists = ["ar1"]
    load_audio_data(audio3, session)

    session.commit()
    g.close()

    app.dependency_overrides[db.get_session] = session_gen
    client = TestClient(app)

    response = client.get("/rest/getAlbumList2?type=alphabeticalByName&u=admin&p=admin")
    assert response.status_code == 200

    data = response.json()
    album_list = data["subsonic-response"]["albumList2"]

    assert len(album_list["album"]) == 3
    assert album_list["album"][0]["name"] == "al2"
    assert album_list["album"][1]["name"] == "al3"
    assert album_list["album"][2]["name"] == "bl1"


def test_get_album_list_alphabetical_by_artist(db_uri: str):
    session_gen = partial(get_session_gen, db_uri=db_uri)
    g = session_gen()
    session = next(g)

    create_user(session, "admin", "admin")

    audio1 = get_default_audio_info("tracks/t1.mp3")
    audio1.title = "track1"
    audio1.album = "al1"
    audio1.artists = ["arb"]
    audio1.album_artist = "arb"
    load_audio_data(audio1, session)

    audio2 = get_default_audio_info("tracks/t2.mp3")
    audio2.title = "track2"
    audio2.album = "al2"
    audio2.artists = ["ara"]
    audio2.album_artist = "ara"
    load_audio_data(audio2, session)

    audio3 = get_default_audio_info("tracks/t3.mp3")
    audio3.title = "track3"
    audio3.album = "al3"
    audio3.artists = ["zz"]
    audio3.album_artist = "zz"
    load_audio_data(audio3, session)

    session.commit()
    g.close()

    app.dependency_overrides[db.get_session] = session_gen
    client = TestClient(app)

    response = client.get(
        "/rest/getAlbumList2?type=alphabeticalByArtist&u=admin&p=admin"
    )
    assert response.status_code == 200

    data = response.json()
    album_list = data["subsonic-response"]["albumList2"]

    assert len(album_list["album"]) == 3
    assert album_list["album"][0]["name"] == "al2"  # ara
    assert album_list["album"][1]["name"] == "al1"  # arb
    assert album_list["album"][2]["name"] == "al3"  # zz


def test_get_album_list_by_year(db_uri: str):
    session_gen = partial(get_session_gen, db_uri=db_uri)
    g = session_gen()
    session = next(g)

    create_user(session, "admin", "admin")

    audio1 = get_default_audio_info("tracks/t1.mp3")
    audio1.title = "track1"
    audio1.album = "al1"
    audio1.year = 2011
    load_audio_data(audio1, session)

    audio2 = get_default_audio_info("tracks/t2.mp3")
    audio2.title = "track2"
    audio2.album = "al2"
    audio2.year = 2005
    load_audio_data(audio2, session)

    audio3 = get_default_audio_info("tracks/t3.mp3")
    audio3.title = "track3"
    audio3.album = "al3"
    audio3.year = 2003
    load_audio_data(audio3, session)

    session.commit()
    g.close()

    app.dependency_overrides[db.get_session] = session_gen
    client = TestClient(app)

    response = client.get(
        "/rest/getAlbumList2?type=byYear&fromYear=2000&toYear=2010&u=admin&p=admin"
    )
    assert response.status_code == 200

    data = response.json()
    album_list = data["subsonic-response"]["albumList2"]

    assert len(album_list["album"]) == 2
    assert album_list["album"][0]["name"] == "al3"  # 2003
    assert album_list["album"][1]["name"] == "al2"  # 2005


def test_get_album_list_by_genre(db_uri: str):
    session_gen = partial(get_session_gen, db_uri=db_uri)
    g = session_gen()
    session = next(g)

    create_user(session, "admin", "admin")

    audio1 = get_default_audio_info("tracks/t1.mp3")
    audio1.title = "track1"
    audio1.album = "al1"
    audio1.genres = ["Rock"]
    load_audio_data(audio1, session)

    audio2 = get_default_audio_info("tracks/t2.mp3")
    audio2.title = "track2"
    audio2.album = "al2"
    audio2.genres = ["Rock"]
    load_audio_data(audio2, session)

    audio3 = get_default_audio_info("tracks/t3.mp3")
    audio3.title = "track3"
    audio3.album = "al3"
    audio3.genres = ["Pop"]
    load_audio_data(audio3, session)

    session.commit()
    g.close()

    app.dependency_overrides[db.get_session] = session_gen
    client = TestClient(app)

    response = client.get("/rest/getAlbumList2?type=byGenre&genre=Rock&u=admin&p=admin")
    assert response.status_code == 200

    data = response.json()
    album_list = data["subsonic-response"]["albumList2"]

    assert len(album_list["album"]) == 2
    assert {a["name"] for a in album_list["album"]} == {"al1", "al2"}


def test_get_album_list_missing_genre(db_uri: str):
    session_gen = partial(get_session_gen, db_uri=db_uri)
    g = session_gen()
    session = next(g)

    create_user(session, "admin", "admin")
    g.close()

    app.dependency_overrides[db.get_session] = session_gen
    client = TestClient(app)

    response = client.get("/rest/getAlbumList2?type=byGenre&u=admin&p=admin")
    assert response.status_code == 400

    data = response.json()
    assert data["detail"] == "Invalid arguments"


def test_get_album_list_missing_year(db_uri: str):
    session_gen = partial(get_session_gen, db_uri=db_uri)
    g = session_gen()
    session = next(g)

    create_user(session, "admin", "admin")
    g.close()

    app.dependency_overrides[db.get_session] = session_gen
    client = TestClient(app)

    response = client.get("/rest/getAlbumList2?type=byYear&u=admin&p=admin")
    assert response.status_code == 400

    data = response.json()
    assert data["detail"] == "Invalid arguments"


def test_search3(db_uri: str):
    session_gen = partial(get_session_gen, db_uri=db_uri)
    g = session_gen()
    session = next(g)

    create_user(session, "admin", "admin")

    audio1 = get_default_audio_info("tracks/t1.mp3")
    audio1.title = "track1"
    audio1.album = "al1"
    audio1.artists = ["ar1"]
    audio1.album_artist = "ar1"
    load_audio_data(audio1, session)

    audio2 = get_default_audio_info("tracks/t2.mp3")
    audio2.title = "song2"
    audio2.album = "al2"
    audio2.artists = ["singer2"]
    audio2.album_artist = "singer2"
    load_audio_data(audio2, session)

    audio3 = get_default_audio_info("tracks/t3.mp3")
    audio3.title = "track32"
    audio3.album = "list3"
    audio3.artists = ["singer3"]
    audio3.album_artist = "singer3"
    load_audio_data(audio3, session)

    session.commit()
    g.close()

    app.dependency_overrides[db.get_session] = session_gen
    client = TestClient(app)

    response = client.get("/rest/search3?query=a&u=admin&p=admin")
    assert response.status_code == 200

    data = response.json()
    search_result = data["subsonic-response"]["searchResult3"]

    assert len(search_result["artist"]) == 1  # ar1
    assert len(search_result["album"]) == 2  # al1, al2
    assert len(search_result["song"]) == 2  # track1, track32

    assert search_result["artist"][0]["name"] == "ar1"

    album_names = {a["name"] for a in search_result["album"]}
    assert "al1" in album_names
    assert "al2" in album_names

    song_titles = {s["title"] for s in search_result["song"]}
    assert "track1" in song_titles
    assert "track32" in song_titles


def test_get_genres(db_uri: str):
    session_gen = partial(get_session_gen, db_uri=db_uri)
    g = session_gen()
    session = next(g)

    create_user(session, "admin", "admin")

    audio1 = get_default_audio_info("tracks/t1.mp3")
    audio1.title = "track1"
    audio1.album = "al1"
    audio1.artists = ["arb"]
    audio1.album_artist = "arb"
    audio1.genres = ["g1", "g2"]
    load_audio_data(audio1, session)

    audio2 = get_default_audio_info("tracks/t2.mp3")
    audio2.title = "track2"
    audio2.album = "al2"
    audio2.artists = ["ara"]
    audio2.album_artist = "ara"
    audio2.genres = ["g1", "g3"]
    load_audio_data(audio2, session)

    audio3 = get_default_audio_info("tracks/t3.mp3")
    audio3.title = "track3"
    audio3.album = "al3"
    audio3.artists = ["zz"]
    audio3.album_artist = "zz"
    audio3.genres = ["g2", "g3"]
    load_audio_data(audio3, session)

    session.commit()
    g.close()

    app.dependency_overrides[db.get_session] = session_gen
    client = TestClient(app)

    response = client.get("/rest/getGenres?u=admin&p=admin")
    assert response.status_code == 200

    data = response.json()
    genres = data["subsonic-response"]["genres"]["genre"]

    assert len(genres) >= 3

    assert genres == [
        {"songCount": 2, "albumCount": 2, "value": "g1"},
        {"songCount": 2, "albumCount": 2, "value": "g2"},
        {"songCount": 2, "albumCount": 2, "value": "g3"},
    ]


def test_get_songs_by_genre(db_uri: str):
    session_gen = partial(get_session_gen, db_uri=db_uri)
    g = session_gen()
    session = next(g)

    create_user(session, "admin", "admin")

    audio1 = get_default_audio_info("tracks/t1.mp3")
    audio1.title = "track1"
    audio1.album = "al1"
    audio1.artists = ["arb"]
    audio1.album_artist = "arb"
    audio1.genres = ["g1", "g2"]
    load_audio_data(audio1, session)

    audio2 = get_default_audio_info("tracks/t2.mp3")
    audio2.title = "track2"
    audio2.album = "al2"
    audio2.artists = ["ara"]
    audio2.album_artist = "ara"
    audio2.genres = ["g1", "g3"]
    load_audio_data(audio2, session)

    audio3 = get_default_audio_info("tracks/t3.mp3")
    audio3.title = "track3"
    audio3.album = "al3"
    audio3.artists = ["zz"]
    audio3.album_artist = "zz"
    audio3.genres = ["g2", "g3"]
    load_audio_data(audio3, session)

    session.commit()
    g.close()

    app.dependency_overrides[db.get_session] = session_gen
    client = TestClient(app)

    response = client.get("/rest/getSongsByGenre?genre=g1&u=admin&p=admin")
    assert response.status_code == 200

    data = response.json()
    songs = data["subsonic-response"]["songsByGenre"]["song"]
    assert len(songs) == 2

    song_titles = {s["title"] for s in songs}
    assert "track1" in song_titles
    assert "track2" in song_titles


def test_star(db_uri: str):
    session_gen = partial(get_session_gen, db_uri=db_uri)
    g = session_gen()
    session = next(g)

    create_user(session, "admin", "admin")

    audio1 = get_default_audio_info("tracks/t1.mp3")
    audio1.title = "track1"
    load_audio_data(audio1, session)

    audio2 = get_default_audio_info("tracks/t2.mp3")
    audio2.title = "track2"
    load_audio_data(audio2, session)

    session.commit()

    app.dependency_overrides[db.get_session] = session_gen
    client = TestClient(app)

    response = client.get("/rest/star?id=1&id=2&u=admin&p=admin")
    assert response.status_code == 200

    fav_tracks = session.exec(select(db.FavouriteTrack)).all()
    assert fav_tracks is not None
    assert len(fav_tracks) == 2
    user_tracks = [(f.user_id, f.track_id) for f in fav_tracks]
    assert (1, 1) in user_tracks
    assert (1, 2) in user_tracks

    g.close()


def test_unstar_track(db_uri: str):
    session_gen = partial(get_session_gen, db_uri=db_uri)
    g = session_gen()
    session = next(g)

    create_user(session, "admin", "admin")
    audio_info = get_default_audio_info()
    load_audio_data(audio_info, session)

    fav_track = db.FavouriteTrack(user_id=1, track_id=1, added_at="")
    session.add(fav_track)
    session.commit()

    app.dependency_overrides[db.get_session] = session_gen
    client = TestClient(app)

    response = client.get("/rest/unstar?id=1&u=admin&p=admin")
    assert response.status_code == 200

    fav_track = session.exec(
        select(db.FavouriteTrack)
        .where(db.FavouriteTrack.user_id == 1)
        .where(db.FavouriteTrack.track_id == 1)
    ).first()
    assert fav_track is None
    g.close()


def test_get_starred2(db_uri: str):
    session_gen = partial(get_session_gen, db_uri=db_uri)
    g = session_gen()
    session = next(g)
    now = datetime.now()

    create_user(session, "admin", "admin")

    audio_info1 = get_default_audio_info()
    audio_info1.artists = ["ar1"]
    audio_info1.title = "track1"
    audio_info1.album_artist = "ar1"
    audio_info1.file_path = "tracks/t1.mp3"
    load_audio_data(audio_info1, session)

    playlist = db.Playlist(
        id=1, name="myplaylist", user_id=1, total_tracks=0, create_date=now
    )
    session.add(playlist)
    session.commit()

    session.add_all(
        [
            db.FavouriteArtist(user_id=1, artist_id=1, added_at=now),
            db.FavouriteAlbum(user_id=1, album_id=1, added_at=now),
            db.FavouriteTrack(user_id=1, track_id=1, added_at=now),
            db.FavouritePlaylist(user_id=1, playlist_id=1, added_at=now),
        ]
    )
    session.commit()
    session.close()
    g.close()

    app.dependency_overrides[db.get_session] = session_gen
    client = TestClient(app)

    response = client.get("/rest/getStarred2?u=admin&p=admin")
    assert response.status_code == 200

    data = response.json()
    starred = data["subsonic-response"]["starred2"]

    assert len(starred["artist"]) == 1
    assert starred["artist"][0]["id"] == "1"
    assert starred["artist"][0]["name"] == "ar1"

    assert len(starred["album"]) == 1
    assert starred["album"][0]["id"] == "1"
    assert starred["album"][0]["name"] == "al1"

    assert len(starred["song"]) == 1
    assert starred["song"][0]["id"] == "1"
    assert starred["song"][0]["title"] == "track1"

    assert len(starred["playlist"]) == 1
    assert starred["playlist"][0]["id"] == "1"
    assert starred["playlist"][0]["name"] == "myplaylist"
