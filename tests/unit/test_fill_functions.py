import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

import src.app.database as db
from src.app import dto
from src.app.service_layer import (
    fill_artist,
    fill_album,
    fill_albums,
    fill_artist_item,
    fill_artist_items,
    fill_genre_item,
    fill_genre_items,
    fill_track,
    fill_tracks,
    fill_genre,
    fill_genres,
    fill_artists,
    fill_playlist,
    fill_playlists,
)


class TestMusicFunctions(unittest.TestCase):

    def create_mock_artist(self, id=1, name="Test Artist", albums=[]):
        mock_artist = MagicMock()
        mock_artist.id = id
        mock_artist.name = name
        mock_artist.albums = albums
        return mock_artist

    def create_mock_album(self, id=1, name="Test Album", total_tracks=10, tracks=[]):
        mock_album = MagicMock()
        mock_album.id = id
        mock_album.name = name
        mock_album.total_tracks = total_tracks
        mock_album.tracks = tracks
        return mock_album

    def create_mock_track(self, id=1, title="Test Track", album_name="Test Album"):
        mock_track = MagicMock()
        mock_track.id = id
        mock_track.title = title
        mock_track.album.name = album_name
        mock_track.album_id = 1
        mock_track.year = "2023"
        mock_track.genres = []
        mock_track.artists = []
        mock_track.file_size = 12345
        mock_track.file_path = "audio/mpeg"
        mock_track.duration = 180
        mock_track.bit_rate = 320
        return mock_track

    def create_mock_playlist(self, id=1, name="My Playlist", total_tracks=2, tracks=[]):
        mock_playlist = MagicMock()
        mock_playlist.id = id
        mock_playlist.name = name
        mock_playlist.total_tracks = total_tracks
        mock_playlist.playlist_tracks = tracks
        return mock_playlist

    @patch("src.app.service_layer.fill_albums")
    def test_fill_artist(self, mock_fill_albums):
        mock_db_artist = self.create_mock_artist()
        mock_fill_albums.return_value = []

        artist = fill_artist(mock_db_artist, None, with_albums=True, with_songs=False)

        self.assertEqual(artist.id, 1)
        self.assertEqual(artist.name, "Test Artist")
        self.assertIsNone(artist.artist_image_url)
        self.assertIsNone(artist.starred)
        self.assertEqual(artist.albums, [])

    @patch("src.app.service_layer.get_album_genres")
    @patch("src.app.service_layer.get_tracklist_duration")
    @patch("src.app.service_layer.join_artist_names")
    @patch("src.app.service_layer.get_album_artist_id_by_album")
    @patch("src.app.service_layer.join_genre_names")
    @patch("src.app.service_layer.fill_artist_items")
    @patch("src.app.service_layer.fill_genre_items")
    def test_fill_album(
        self,
        mock_fill_genre_items,
        mock_fill_artist_items,
        mock_join_genre_names,
        mock_get_album_artist_id_by_album,
        mock_join_artist_names,
        mock_get_tracklist_duration,
        mock_get_album_genres,
    ):
        mock_db_album = self.create_mock_album()
        mock_get_album_genres.return_value = []
        mock_get_tracklist_duration.return_value = 3600
        mock_join_artist_names.return_value = "Test Artist"
        mock_get_album_artist_id_by_album.return_value = 2
        mock_join_genre_names.return_value = ""
        mock_fill_artist_items.return_value = []
        mock_fill_genre_items.return_value = []

        album = fill_album(mock_db_album, None, with_songs=False)

        self.assertEqual(album.id, 1)
        self.assertEqual(album.name, "Test Album")
        self.assertEqual(album.song_count, 10)
        self.assertEqual(album.duration, 3600)
        self.assertEqual(album.created.date(), datetime.now().date())
        self.assertEqual(album.artist, "Test Artist")
        self.assertEqual(album.artist_id, 2)
        self.assertEqual(album.cover_art_id, 1)
        self.assertIsNone(album.play_count)
        self.assertIsNone(album.starred)
        self.assertIsNone(album.year)
        self.assertEqual(album.genre, "")
        self.assertEqual(album.artists, [])
        self.assertEqual(album.genres, [])
        self.assertEqual(album.tracks, [])

    @patch("src.app.service_layer.fill_album")
    def test_fill_albums(self, mock_fill_album):
        mock_db_album1 = self.create_mock_album(id=1, name="Album 1", total_tracks=5)
        mock_db_album2 = self.create_mock_album(id=2, name="Album 2", total_tracks=10)
        db_albums = [mock_db_album1, mock_db_album2]

        mock_fill_album.side_effect = [
            dto.Album(
                id=1,
                name="Album 1",
                song_count=5,
                duration=3000,
                created=datetime.now(),
                artist="Artist 1",
                artist_id=1,
                cover_art_id=1,
                play_count=None,
                starred=None,
                year=None,
                genre="",
                artists=[],
                genres=[],
                tracks=[],
            ),
            dto.Album(
                id=2,
                name="Album 2",
                song_count=10,
                duration=6000,
                created=datetime.now(),
                artist="Artist 2",
                artist_id=2,
                cover_art_id=2,
                play_count=None,
                starred=None,
                year=None,
                genre="",
                artists=[],
                genres=[],
                tracks=[],
            ),
        ]

        albums = fill_albums(db_albums, None, with_songs=False)

        self.assertEqual(len(albums), 2)
        self.assertEqual(albums[0].id, 1)
        self.assertEqual(albums[1].id, 2)

    def test_fill_artist_item(self):
        mock_db_artist = self.create_mock_artist(id=1, name="Test Artist")
        artist_item = fill_artist_item(mock_db_artist)

        self.assertEqual(artist_item.id, 1)
        self.assertEqual(artist_item.name, "Test Artist")

    def test_fill_artist_items(self):
        db_artists = [
            self.create_mock_artist(id=1, name="Artist 1"),
            self.create_mock_artist(id=2, name="Artist 2"),
        ]

        artist_items = fill_artist_items(db_artists)

        self.assertEqual(len(artist_items), 2)
        self.assertEqual(artist_items[0].id, 1)
        self.assertEqual(artist_items[1].id, 2)

    def test_fill_genre_item(self):
        mock_db_genre = MagicMock()
        mock_db_genre.name = "Test Genre"

        genre_item = fill_genre_item(mock_db_genre)

        self.assertEqual(genre_item.name, "Test Genre")

    def test_fill_genre_items(self):
        mock_db_genre1 = MagicMock()
        mock_db_genre1.name = "Genre 1"
        mock_db_genre2 = MagicMock()
        mock_db_genre2.name = "Genre 2"
        db_genres = [mock_db_genre1, mock_db_genre2]

        genre_items = fill_genre_items(db_genres)

        self.assertEqual(len(genre_items), 2)
        self.assertEqual(genre_items[0].name, "Genre 1")
        self.assertEqual(genre_items[1].name, "Genre 2")

    @patch("src.app.service_layer.fill_artist_items")
    @patch("src.app.service_layer.fill_genre_items")
    def test_fill_track(self, mock_fill_genre_items, mock_fill_artist_items):
        mock_db_track = self.create_mock_track()
        mock_fill_artist_items.return_value = []
        mock_fill_genre_items.return_value = []

        track = fill_track(mock_db_track, db.User(id=1, name="Test User"))

        self.assertEqual(track.id, 1)
        self.assertEqual(track.title, "Test Track")
        self.assertEqual(track.album, "Test Album")
        self.assertEqual(track.album_id, 1)
        self.assertEqual(track.year, 2023)
        self.assertEqual(track.file_size, 12345)
        self.assertEqual(track.path, "audio/mpeg")
        self.assertEqual(track.duration, 180)
        self.assertEqual(track.bit_rate, 320)

    def test_fill_tracks(self):
        mock_db_tracks = [self.create_mock_track() for _ in range(2)]
        result = fill_tracks(mock_db_tracks, db.User(id=1, name="Test User"))
        self.assertEqual(len(result), 2)

    def test_fill_genre(self):
        mock_db_track = self.create_mock_track()
        mock_genre = MagicMock()
        mock_genre.name = "Rock"
        mock_genre.tracks = [mock_db_track, mock_db_track]
        result = fill_genre(mock_genre)
        self.assertEqual(result.name, "Rock")
        self.assertEqual(result.albumCount, 1)
        self.assertEqual(result.songCount, 2)

    def test_fill_genres(self):
        mock_genre = MagicMock()
        mock_genre.name = "Rock"
        db_genres = [mock_genre]
        result = fill_genres(db_genres)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, "Rock")

    def test_fill_artists(self):
        db_artists = [self.create_mock_artist()]
        result = fill_artists(db_artists, db.User(id=1, name="Test User"))
        self.assertEqual(len(result), 1)

    def test_fill_playlist(self):
        mock_db_track = self.create_mock_track()
        mock_playlist = self.create_mock_playlist(tracks=[mock_db_track])
        result = fill_playlist(
            mock_playlist, db.User(id=1, name="Test User"), with_songs=True
        )
        self.assertEqual(result.name, "My Playlist")
        self.assertEqual(result.song_count, 2)

    def test_fill_playlists(self):
        mock_db_track = self.create_mock_track()
        mock_playlist = self.create_mock_playlist(tracks=[mock_db_track])
        db_playlists = [mock_playlist]
        result = fill_playlists(
            db_playlists, db.User(id=1, name="Test User"), with_songs=True
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, "My Playlist")


if __name__ == "__main__":
    unittest.main()
