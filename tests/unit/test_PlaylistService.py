import unittest
from unittest.mock import MagicMock, patch

from src.app.service_layer import PlaylistService


class TestPlaylistService(unittest.TestCase):
    def setUp(self):
        self.session_mock = MagicMock()
        self.playlist_service = PlaylistService(self.session_mock)

    def test_get_playlists_returns_list(self):
        self.playlist_service.playlist_db_helper.get_all_playlists = MagicMock(
            return_value=[MagicMock(id=i) for i in range(3)]
        )
        result = self.playlist_service.get_playlists()
        assert len(result) == 3

    def test_get_playlists_returns_empty_list(self):
        self.playlist_service.playlist_db_helper.get_all_playlists = MagicMock(
            return_value=[]
        )
        result = self.playlist_service.get_playlists()
        assert result == []

    def test_get_playlist_by_id_found(self):
        playlist_mock = MagicMock(id=1)
        self.playlist_service.playlist_db_helper.get_playlist = MagicMock(
            return_value=playlist_mock
        )
        with patch("src.app.service_layer.fill_playlist", return_value=playlist_mock):
            result = self.playlist_service.get_playlist(1)
            self.assertIsNotNone(result)
            assert result.id == 1

    def test_get_playlist_by_id_not_found(self):
        self.playlist_service.playlist_db_helper.get_playlist = MagicMock(
            return_value=None
        )
        result = self.playlist_service.get_playlist(999)
        self.assertIsNone(result)

    def test_create_playlist_success(self):
        user_mock = MagicMock()
        playlist_mock = MagicMock(id=1)
        playlist_mock.name = "Test Playlist"
        self.playlist_service.playlist_db_helper.create_playlist = MagicMock(
            return_value=playlist_mock
        )
        with patch("src.app.service_layer.fill_playlist", return_value=playlist_mock):
            result = self.playlist_service.create_playlist(
                "Test Playlist", [], user_mock
            )
            assert result.id == 1
            assert result.name == "Test Playlist"

    def test_delete_playlist_success(self):
        user_mock = MagicMock()
        self.playlist_service.playlist_db_helper.delete_playlist = MagicMock(
            return_value=True
        )
        result = self.playlist_service.delete_playlist(1, user_mock)
        self.assertTrue(result)

    def test_delete_playlist_not_found(self):
        user_mock = MagicMock()
        self.playlist_service.playlist_db_helper.delete_playlist = MagicMock(
            return_value=False
        )
        result = self.playlist_service.delete_playlist(999, user_mock)
        self.assertFalse(result)

    def test_update_playlist_success(self):
        self.playlist_service.playlist_db_helper.update_playlist = MagicMock(
            return_value=True
        )
        result = self.playlist_service.update_playlist(1, "New Playlist", [2, 3], [4])
        self.assertTrue(result)

    def test_update_playlist_not_found(self):
        self.playlist_service.playlist_db_helper.update_playlist = MagicMock(
            return_value=False
        )
        result = self.playlist_service.update_playlist(999, "New Playlist", [2, 3], [4])
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
