import unittest
from unittest.mock import MagicMock

import src.app.database as db
import src.app.dto as dto
from src.app.service_layer import AlbumService, RequestType

from src.app.service_layer import fill_album


def get_entities(
    i: int, artist_name: str = "abc"
) -> tuple[db.Album, db.Track, db.Artist]:
    album = db.Album(
        id=i,
        name=f"album{i}",
        total_tracks=1,
    )

    track = db.Track(
        id=i,
        file_path=f"./track{i}.mp3",
        file_size=1984500,
        type="audio/mpeg",
        title=f"track{i}",
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

    artist = db.Artist(
        id=i,
        name=artist_name,
        tracks=[track],
        albums=[album],
    )

    return (album, track, artist)


class TestTrackService(unittest.TestCase):
    def setUp(self):
        self.session_mock = MagicMock()
        self.album_service = AlbumService(self.session_mock)

    def test_fill_album_without_songs(self):
        album, track, artist = get_entities(1)

        result = fill_album(album, None, with_songs=False)

        self.assertEqual(result.id, album.id)
        self.assertEqual(result.name, album.name)
        self.assertEqual(len(result.tracks), 0)

    def test_fill_album_with_songs(self):
        album, track, artist = get_entities(1)

        result = fill_album(album, None, with_songs=True)

        self.assertEqual(result.id, album.id)
        self.assertEqual(result.name, album.name)

        self.assertEqual(len(result.tracks), 1)
        track0 = result.tracks[0]
        self.assertEqual(track0.id, track.id)
        self.assertEqual(track0.title, track.title)

    def test_get_album_by_id(self):
        album, track, artist = get_entities(1)

        self.album_service.album_db_helper.get_album_by_id = MagicMock(
            return_value=album
        )

        result: dto.Album | None = self.album_service.get_album_by_id(1)

        self.assertIsNotNone(result)
        expected = fill_album(album, None, with_songs=True)
        self.assertEqual(result, expected)

    def test_get_album_by_id_not_found(self):
        self.album_service.album_db_helper.get_album_by_id = MagicMock(
            return_value=None
        )

        result: dto.Album | None = self.album_service.get_album_by_id(1)

        self.assertIsNone(result)

    def test_get_album_list_random_one(self):
        album, track, artist = get_entities(1)

        self.album_service.album_db_helper.get_all_albums = MagicMock(
            return_value=[album]
        )

        result = self.album_service.get_album_list(RequestType.RANDOM, 1, 0)

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)

        expected = fill_album(album, None, with_songs=False)
        self.assertEqual(result[0], expected)


if __name__ == "__main__":
    unittest.main()
