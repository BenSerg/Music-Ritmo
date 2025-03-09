import unittest
from unittest.mock import MagicMock

import src.app.database as db
from src.app.service_layer import StarService


class TestStarService(unittest.TestCase):
    def setUp(self):
        self.session_mock = MagicMock()
        self.star_service = StarService(self.session_mock)
        self.user = db.User(id=1, name="Test User")
        self.track_ids = [1, 2, 3]

        self._setup_mocks()

    def _setup_mocks(self):
        self.star_service.favourite_db_helper.star_track = MagicMock()
        self.star_service.favourite_db_helper.unstar_track = MagicMock()
        self.star_service.favourite_db_helper.get_starred_tracks = MagicMock()
        self.star_service.favourite_db_helper.get_starred_albums = MagicMock()
        self.star_service.favourite_db_helper.get_starred_artists = MagicMock()
        self.star_service.favourite_db_helper.get_starred_playlists = MagicMock()

    def test_star_tracks(self):
        self.star_service.star(self.track_ids, [], [], [], self.user)

        for track_id in self.track_ids:
            self.star_service.favourite_db_helper.star_track.assert_any_call(
                track_id, self.user.id
            )

    def test_unstar_tracks(self):
        self.star_service.unstar(self.track_ids, [], [], [], self.user)

        for track_id in self.track_ids:
            self.star_service.favourite_db_helper.unstar_track.assert_any_call(
                track_id, self.user.id
            )

    @staticmethod
    def _create_mock_track(track_id, title, album):
        return db.Track(
            id=track_id,
            file_path=f"./track{track_id}.mp3",
            file_size=1984500,
            type="audio/mpeg",
            title=title,
            album=album,
            plays_count=0,
            cover=b"",
            cover_type="",
            bit_rate=128,
            bits_per_sample=3,
            sample_rate=44100,
            channels=2,
            duration=60,
        )

    def _create_mock_tracks(self):
        album = db.Album(id=1, name="album1", total_tracks=2)
        track_1 = self._create_mock_track(1, "track1", album)
        track_2 = self._create_mock_track(2, "track2", album)
        return [track_1, track_2], album

    def test_get_starred_with_tracks_and_albums(self):
        db_tracks, album = self._create_mock_tracks()
        artist = db.Artist(id=1, name="name", tracks=db_tracks, albums=[album])

        self.star_service.favourite_db_helper.get_starred_tracks.return_value = (
            db_tracks
        )
        self.star_service.favourite_db_helper.get_starred_albums.return_value = [album]
        self.star_service.favourite_db_helper.get_starred_artists.return_value = [
            artist
        ]
        self.star_service.favourite_db_helper.get_starred_playlists.return_value = [
            MagicMock()
        ]

        result = self.star_service.get_starred(self.user)

        self.assertEqual(len(result[0]), len(db_tracks))
        self.assertEqual(len(result[1]), 1)
        self.assertEqual(len(result[2]), 1)
        self.assertEqual(len(result[3]), 1)

        for i, track in enumerate(result[0]):
            self.assertEqual(track.id, db_tracks[i].id)
            self.assertEqual(track.title, db_tracks[i].title)
            self.assertEqual(track.album, db_tracks[i].album.name)

        returned_album = result[1][0]
        self.assertEqual(returned_album.id, album.id)
        self.assertEqual(returned_album.name, album.name)

        returned_artist = result[2][0]
        self.assertEqual(returned_artist.id, artist.id)
        self.assertEqual(returned_artist.name, artist.name)

    def test_get_starred_with_no_tracks(self):
        self.star_service.favourite_db_helper.get_starred_tracks.return_value = []
        self.star_service.favourite_db_helper.get_starred_albums.return_value = []
        self.star_service.favourite_db_helper.get_starred_artists.return_value = []
        self.star_service.favourite_db_helper.get_starred_playlists.return_value = []

        result = self.star_service.get_starred(self.user)

        self.assertEqual(len(result[0]), 0)
        self.assertEqual(len(result[1]), 0)
        self.assertEqual(len(result[2]), 0)
        self.assertEqual(len(result[3]), 0)

    def test_get_starred_with_multiple_items(self):
        db_tracks, album = self._create_mock_tracks()
        track_3 = self._create_mock_track(3, "track3", album)
        artist_1 = db.Artist(id=1, name="artist1", tracks=db_tracks, albums=[album])
        artist_2 = db.Artist(id=2, name="artist2", tracks=[track_3], albums=[album])

        self.star_service.favourite_db_helper.get_starred_tracks.return_value = (
            db_tracks + [track_3]
        )
        self.star_service.favourite_db_helper.get_starred_albums.return_value = [album]
        self.star_service.favourite_db_helper.get_starred_artists.return_value = [
            artist_1,
            artist_2,
        ]
        self.star_service.favourite_db_helper.get_starred_playlists.return_value = [
            MagicMock()
        ]

        result = self.star_service.get_starred(self.user)

        self.assertEqual(len(result[0]), len(db_tracks) + 1)
        self.assertEqual(len(result[1]), 1)
        self.assertEqual(len(result[2]), 2)
        self.assertEqual(len(result[3]), 1)

    def test_get_starred_with_empty_artist(self):
        db_tracks, album = self._create_mock_tracks()
        empty_artist = db.Artist(id=1, name="empty_artist", tracks=[], albums=[album])

        self.star_service.favourite_db_helper.get_starred_tracks.return_value = (
            db_tracks
        )
        self.star_service.favourite_db_helper.get_starred_albums.return_value = [album]
        self.star_service.favourite_db_helper.get_starred_artists.return_value = [
            empty_artist
        ]
        self.star_service.favourite_db_helper.get_starred_playlists.return_value = [
            MagicMock()
        ]

        result = self.star_service.get_starred(self.user)

        self.assertEqual(len(result[0]), len(db_tracks))
        self.assertEqual(len(result[1]), 1)
        self.assertEqual(len(result[2]), 1)
        self.assertEqual(len(result[3]), 1)

        returned_artist = result[2][0]
        self.assertEqual(returned_artist.id, empty_artist.id)
        self.assertEqual(returned_artist.name, empty_artist.name)

    def test_get_starred_with_only_playlists(self):
        self.star_service.favourite_db_helper.get_starred_tracks.return_value = []
        self.star_service.favourite_db_helper.get_starred_albums.return_value = []
        self.star_service.favourite_db_helper.get_starred_artists.return_value = []
        self.star_service.favourite_db_helper.get_starred_playlists.return_value = [
            MagicMock()
        ]

        result = self.star_service.get_starred(self.user)

        self.assertEqual(len(result[0]), 0)
        self.assertEqual(len(result[1]), 0)
        self.assertEqual(len(result[2]), 0)
        self.assertEqual(len(result[3]), 1)

    def test_get_starred_with_various_scenarios(self):
        db_tracks, album = self._create_mock_tracks()
        artist_1 = db.Artist(id=1, name="artist1", tracks=db_tracks, albums=[album])
        artist_2 = db.Artist(id=2, name="artist2", tracks=[], albums=[album])
        track_3 = self._create_mock_track(3, "track3", album)

        self.star_service.favourite_db_helper.get_starred_tracks.return_value = (
            db_tracks + [track_3]
        )
        self.star_service.favourite_db_helper.get_starred_albums.return_value = [album]
        self.star_service.favourite_db_helper.get_starred_artists.return_value = [
            artist_1,
            artist_2,
        ]
        self.star_service.favourite_db_helper.get_starred_playlists.return_value = [
            MagicMock()
        ]

        result = self.star_service.get_starred(self.user)

        self.assertEqual(len(result[0]), len(db_tracks) + 1)
        self.assertEqual(len(result[1]), 1)
        self.assertEqual(len(result[2]), 2)
        self.assertEqual(len(result[3]), 1)

        for i, track in enumerate(result[0]):
            self.assertEqual(track.id, (db_tracks + [track_3])[i].id)
            self.assertEqual(track.title, (db_tracks + [track_3])[i].title)
            self.assertEqual(track.album, (db_tracks + [track_3])[i].album.name)

        returned_album = result[1][0]
        self.assertEqual(returned_album.id, album.id)
        self.assertEqual(returned_album.name, album.name)

        for i, artist in enumerate(result[2]):
            if i == 0:
                self.assertEqual(artist.id, artist_1.id)
                self.assertEqual(artist.name, artist_1.name)
            else:
                self.assertEqual(artist.id, artist_2.id)
                self.assertEqual(artist.name, artist_2.name)

        self.assertEqual(len(result[3]), 1)


if __name__ == "__main__":
    unittest.main()
