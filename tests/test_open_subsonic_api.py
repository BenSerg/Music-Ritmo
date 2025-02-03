from src.app.main import app
from src.app import database as db
from fastapi.testclient import TestClient
from sqlmodel import Session

client = TestClient(app)


def test_ping():
    response = client.get("/rest/ping")
    assert response.status_code == 200

    rsp = response.json()["subsonic-response"]
    assert rsp["status"] == "ok"
    assert rsp["type"] == "MusicRitmo"
    assert rsp["openSubsonic"] == True
    assert rsp["version"] is not None
    assert rsp["serverVersion"] is not None


def test_getPlaylists():
    with Session(db.engine) as session:
        user = db.User(login="test_user", password="password", avatar="line")
        session.add(user)
        session.commit()

        playlist = db.Playlist(
            name="My Playlist",
            user_id=user.id,
            total_tracks=10,
            create_date="2025-01-01",
        )
        session.add(playlist)
        session.commit()

        assert user.id is not None
        assert playlist.user_id == user.id

    response = client.get("/rest/getPlaylists")
    assert response.status_code == 200

    data = response.json()

    subsonic_response = data["subsonic-response"]
    playlists = subsonic_response["playlists"]["playlist"]
    assert len(playlists) > 0

    playlist = playlists[0]
    assert playlist["name"] == "My Playlist"
    assert playlist["owner"] == user.id
    assert playlist["songCount"] == 10
    assert playlist["createDate"] == "2025-01-01"


def test_get_tracks_by_genre():
    response = client.get("/rest/getSongsByGenre?genre=Soundtrack")

    assert response.status_code == 200
    data = response.json()["subsonic-response"]
    assert "songsByGenre" in data
    assert len(data["songsByGenre"]["song"]) == 2


def test_get_random_songs_no_filters():
    response = client.get("/rest/getRandomSongs?size=2")
    assert response.status_code == 200
    assert len(response.json()["subsonic-response"]["randomSongs"]["song"]) == 2


def test_get_random_songs_with_year_filter():
    response = client.get("/rest/getRandomSongs?size=2&fromYear=2024")
    assert response.status_code == 200
    assert len(response.json()["subsonic-response"]["randomSongs"]["song"]) == 2

    response = client.get("/rest/getRandomSongs?size=2&toYear=2010")
    assert not response.json()["subsonic-response"]["randomSongs"]["song"]
