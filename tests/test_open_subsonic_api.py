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
            create_date="2025-01-01"
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
    assert "track" in data
    assert len(data["track"]) == 2

    first_track = {'id': '5', 'parent': '', 'title': 'Arlekino (Geoffrey Day Remix)', 'isDir': False,
                   'isVideo': False, 'type': 'audio/flac', 'albumId': '3',
                   'album': "id=3 year='2023' name='Atomic Heart (Original Game Soundtrack)' total_tracks=2",
                   'artistId': '', 'artist': '', 'coverArt': None, 'duration': 262.25895691609975, 'bitRate': 0,
                   'bitDepth': 16, 'samplingRate': 44100, 'channelCount': 2, 'userRating': 0, 'averageRating': 0.0,
                   'track': 1, 'year': "2023", 'genre': None, 'size': 0, 'discNumber': 1, 'suffix': '',
                   'contentType': 'audio/mpeg',
                   'path': './tracks/Atomic Heart/03. Arlekino (Geoffrey Day Remix).flac'}

    second_track = {'id': '6', 'parent': '', 'title': 'Trava u Doma (Geoffrey Day Remix)', 'isDir': False,
                    'isVideo': False, 'type': 'audio/flac', 'albumId': '3',
                    'album': "id=3 year='2023' name='Atomic Heart (Original Game Soundtrack)' total_tracks=2",
                    'artistId': '', 'artist': '', 'coverArt': None, 'duration': 235.682947845805, 'bitRate': 0,
                    'bitDepth': 16, 'samplingRate': 44100, 'channelCount': 2, 'userRating': 0, 'averageRating': 0.0,
                    'track': 1, 'year': "2023", 'genre': None, 'size': 0, 'discNumber': 1, 'suffix': '',
                    'contentType': 'audio/mpeg',
                    'path': './tracks/Atomic Heart/02. Trava u Doma (Geoffrey Day Remix).flac'}

    assert [first_track, second_track] == data["track"]
