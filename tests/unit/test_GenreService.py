import unittest
from unittest.mock import MagicMock, patch

from src.app import dto
from src.app.service_layer import GenreService, fill_genres, fill_genre


class TestGenreFunctions(unittest.TestCase):

    def test_fill_genre(self):
        mock_db_genre = MagicMock()
        mock_db_genre.name = "Rock"
        mock_db_genre.tracks = [
            MagicMock(album_id=1),
            MagicMock(album_id=1),
            MagicMock(album_id=2),
            MagicMock(album_id=3),
        ]

        expected_genre = dto.Genre(albumCount=3, songCount=4, name="Rock")
        result = fill_genre(mock_db_genre)

        self.assertEqual(result.albumCount, expected_genre.albumCount)
        self.assertEqual(result.songCount, expected_genre.songCount)
        self.assertEqual(result.name, expected_genre.name)

    def test_fill_genres(self):

        mock_db_genre1 = MagicMock(name="Pop")
        mock_db_genre1.tracks = [MagicMock(album_id=1), MagicMock(album_id=2)]

        mock_db_genre2 = MagicMock(name="Jazz")
        mock_db_genre2.tracks = [
            MagicMock(album_id=1),
            MagicMock(album_id=1),
            MagicMock(album_id=2),
        ]

        db_genres = [mock_db_genre1, mock_db_genre2]

        result = fill_genres(db_genres)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].albumCount, 2)
        self.assertEqual(result[0].songCount, 2)
        self.assertEqual(result[1].albumCount, 2)
        self.assertEqual(result[1].songCount, 3)

    def test_fill_genre_empty_tracks(self):
        mock_db_genre = MagicMock()
        mock_db_genre.name = "Classical"
        mock_db_genre.tracks = []

        expected_genre = dto.Genre(albumCount=0, songCount=0, name="Classical")
        result = fill_genre(mock_db_genre)

        self.assertEqual(result.albumCount, expected_genre.albumCount)
        self.assertEqual(result.songCount, expected_genre.songCount)
        self.assertEqual(result.name, expected_genre.name)

    def test_fill_genres_with_empty_genre(self):
        mock_db_genre1 = MagicMock()
        mock_db_genre1.name = "Pop"
        mock_db_genre1.tracks = [MagicMock(album_id=1), MagicMock(album_id=2)]

        mock_db_genre2 = MagicMock()
        mock_db_genre2.name = "Classical"
        mock_db_genre2.tracks = []

        db_genres = [mock_db_genre1, mock_db_genre2]

        result = fill_genres(db_genres)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].albumCount, 2)
        self.assertEqual(result[0].songCount, 2)
        self.assertEqual(result[1].albumCount, 0)
        self.assertEqual(result[1].songCount, 0)

    def test_fill_genres_empty_list(self):
        db_genres = []

        result = fill_genres(db_genres)

        self.assertEqual(result, [])


class TestGenreService(unittest.TestCase):

    @patch("src.app.db_helpers.GenresDBHelper")
    def test_get_genres(self, MockGenresDBHelper):
        mock_session = MagicMock()
        mock_db_genre = MagicMock()
        mock_db_genre.name = "Rock"
        mock_db_genre.tracks = [MagicMock(album_id=1), MagicMock(album_id=2)]

        MockGenresDBHelper.return_value.get_all_genres.return_value = [mock_db_genre]

        genre_service = GenreService(mock_session)
        result = genre_service.get_genres()
        print(result)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, "Rock")
        self.assertEqual(result[0].albumCount, 2)
        self.assertEqual(result[0].songCount, 2)


if __name__ == "__main__":
    unittest.main()
