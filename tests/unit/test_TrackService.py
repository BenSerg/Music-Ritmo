import unittest
from unittest.mock import MagicMock

from src.app.service_layer import TrackService


class TestTrackService(unittest.TestCase):
    def setUp(self):
        self.session_mock = MagicMock()
        self.track_service = TrackService(self.session_mock)

    def test_get_open_subsonic_format(self):
        track_mock = MagicMock()
        track_mock.id = "1"
        track_mock.album_id = 1
        track_mock.title = "Test Track"
        track_mock.album.name = "Test Album"
        track_mock.artists = []
        track_mock.file_size = 123456
        track_mock.type = "audio/mpeg"
        track_mock.duration = 300
        track_mock.bit_rate = 320
        track_mock.bits_per_sample = 16
        track_mock.sample_rate = 44100
        track_mock.channels = 2
        track_mock.file_path = "/path/to/file.mp3"
        track_mock.plays_count = 10
        track_mock.year = "2023"
        track_mock.track_favourites = []

        result = self.track_service.get_open_subsonic_format(track_mock)

        self.assertEqual(result["id"], "1")
        self.assertEqual(result["title"], "Test Track")
        self.assertEqual(result["album"], "Test Album")
        self.assertEqual(result["size"], 123456)
        self.assertEqual(result["duration"], 300)

    def test_get_song_by_id_found(self):

        track_mock = MagicMock()
        track_mock.id = "2"
        self.track_service.DBHelper.get_track_by_id = MagicMock(return_value=track_mock)

        result = self.track_service.get_song_by_id(1)

        self.assertIsNotNone(result)
        self.assertEqual(result["id"], track_mock.id)

    def test_get_song_by_id_not_found(self):
        self.track_service.DBHelper.get_track_by_id = MagicMock(return_value=None)

        result = self.track_service.get_song_by_id(999)

        self.assertIsNone(result)

    def test_get_songs_by_genre(self):
        genre_mock = MagicMock()
        genre_mock.tracks = [MagicMock(id=i) for i in range(5)]

        self.track_service.genre_helper.get_genres_by_name = MagicMock(
            return_value=[genre_mock]
        )

        results = self.track_service.get_songs_by_genre("Rock")

        self.assertEqual(len(results), 5)

    def test_get_random_songs(self):
        tracks_mock = [MagicMock(year=2020) for _ in range(20)]

        self.track_service.DBHelper.get_all_tracks = MagicMock(return_value=tracks_mock)

        results = self.track_service.get_random_songs(size=5)

        self.assertEqual(len(results), 5)

    def test_get_random_songs_with_year_filter(self):
        tracks_mock = [
            MagicMock(year="2020"),
            MagicMock(year="2021"),
            MagicMock(year="2019"),
            MagicMock(year="2018"),
            MagicMock(year="2022"),
        ]

        self.track_service.DBHelper.get_all_tracks = MagicMock(return_value=tracks_mock)

        results = self.track_service.get_random_songs(size=5, from_year="2020")

        for track in results:
            self.assertTrue(track["year"] >= "2020")


if __name__ == "__main__":
    unittest.main()
