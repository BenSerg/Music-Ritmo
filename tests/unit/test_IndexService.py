import unittest
from unittest.mock import MagicMock

from datetime import datetime

import src.app.database as db
import src.app.dto as dto
from src.app.service_layer import IndexService


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


class TestIndexService(unittest.TestCase):
    def setUp(self):
        self.session_mock = MagicMock()
        self.index_service = IndexService(self.session_mock)

    def test_indexes_artist_no_artists(self):
        self.index_service.artist_db_helper.get_all_artists = MagicMock(return_value=[])

        result: dto.Indexes = self.index_service.get_indexes_artists(with_childs=False)

        self.assertIsInstance(result.last_modified, datetime)
        self.assertEqual(len(result.shortcuts), 0)
        self.assertEqual(len(result.tracks), 0)
        self.assertEqual(len(result.artist_index), 0)

    def test_indexes_artist_one(self):
        album, track, artist = get_entities(1)

        self.index_service.artist_db_helper.get_all_artists = MagicMock(
            return_value=[artist]
        )

        result: dto.Indexes = self.index_service.get_indexes_artists(with_childs=False)

        self.assertIsInstance(result.last_modified, datetime)
        self.assertEqual(len(result.shortcuts), 0)
        self.assertEqual(len(result.tracks), 0)

        self.assertEqual(len(result.artist_index), 1)
        artist_index0 = result.artist_index[0]
        self.assertEqual(artist_index0.name, artist.name[0])

        self.assertEqual(len(artist_index0.artist), 1)
        artist_index0_artist = artist_index0.artist[0]
        self.assertEqual(artist_index0_artist.id, artist.id)
        self.assertEqual(artist_index0_artist.name, artist.name)

        self.assertEqual(len(artist_index0_artist.albums), 1)
        artist_index0_artist_album = artist_index0_artist.albums[0]
        self.assertEqual(artist_index0_artist_album.id, album.id)
        self.assertEqual(artist_index0_artist_album.name, album.name)

    def test_indexes_artist_one_with_childs(self):
        album, track, artist = get_entities(1)

        self.index_service.artist_db_helper.get_all_artists = MagicMock(
            return_value=[artist]
        )
        self.index_service.track_db_helper.get_all_tracks = MagicMock(
            return_value=[track]
        )

        result: dto.Indexes = self.index_service.get_indexes_artists(with_childs=True)

        self.assertIsInstance(result.last_modified, datetime)
        self.assertEqual(len(result.shortcuts), 0)

        self.assertEqual(len(result.artist_index), 1)
        artist_index0 = result.artist_index[0]
        self.assertEqual(artist_index0.name, artist.name[0])

        self.assertEqual(len(artist_index0.artist), 1)
        artist_index0_artist = artist_index0.artist[0]
        self.assertEqual(artist_index0_artist.id, artist.id)
        self.assertEqual(artist_index0_artist.name, artist.name)

        self.assertEqual(len(artist_index0_artist.albums), 1)
        artist_index0_artist_album = artist_index0_artist.albums[0]
        self.assertEqual(artist_index0_artist_album.id, album.id)
        self.assertEqual(artist_index0_artist_album.name, album.name)

        self.assertEqual(len(result.tracks), 1)
        track0 = result.tracks[0]
        self.assertEqual(track0.id, track.id)
        self.assertEqual(track0.title, track.title)

    def test_indexes_artist_two_same_letter(self):
        album1, track1, artist1 = get_entities(1, artist_name="aa")
        album2, track2, artist2 = get_entities(2, artist_name="az")

        self.index_service.artist_db_helper.get_all_artists = MagicMock(
            return_value=[artist1, artist2]
        )

        result: dto.Indexes = self.index_service.get_indexes_artists(with_childs=False)

        self.assertIsInstance(result.last_modified, datetime)
        self.assertEqual(len(result.shortcuts), 0)
        self.assertEqual(len(result.tracks), 0)

        self.assertEqual(len(result.artist_index), 1)
        artist_index0 = result.artist_index[0]
        self.assertEqual(artist_index0.name, artist1.name[0])

        self.assertEqual(len(artist_index0.artist), 2)
        artist_index0_artist1 = artist_index0.artist[0]
        self.assertEqual(artist_index0_artist1.id, artist1.id)
        self.assertEqual(artist_index0_artist1.name, artist1.name)

        self.assertEqual(len(artist_index0_artist1.albums), 1)
        artist_index0_artist_album = artist_index0_artist1.albums[0]
        self.assertEqual(artist_index0_artist_album.id, album1.id)
        self.assertEqual(artist_index0_artist_album.name, album1.name)

        artist_index0_artist2 = artist_index0.artist[1]
        self.assertEqual(artist_index0_artist2.id, artist2.id)
        self.assertEqual(artist_index0_artist2.name, artist2.name)

        self.assertEqual(len(artist_index0_artist2.albums), 1)
        artist_index0_artist2_album = artist_index0_artist2.albums[0]
        self.assertEqual(artist_index0_artist2_album.id, album2.id)
        self.assertEqual(artist_index0_artist2_album.name, album2.name)

    def test_indexes_artist_two_different_letters(self):
        album1, track1, artist1 = get_entities(1, artist_name="aa")
        album2, track2, artist2 = get_entities(2, artist_name="bz")

        self.index_service.artist_db_helper.get_all_artists = MagicMock(
            return_value=[artist1, artist2]
        )

        result: dto.Indexes = self.index_service.get_indexes_artists(with_childs=False)

        self.assertIsInstance(result.last_modified, datetime)
        self.assertEqual(len(result.shortcuts), 0)
        self.assertEqual(len(result.tracks), 0)

        self.assertEqual(len(result.artist_index), 2)
        artist_index0 = result.artist_index[0]
        self.assertEqual(artist_index0.name, artist1.name[0])

        self.assertEqual(len(artist_index0.artist), 1)
        artist_index0_artist1 = artist_index0.artist[0]
        self.assertEqual(artist_index0_artist1.id, artist1.id)
        self.assertEqual(artist_index0_artist1.name, artist1.name)

        self.assertEqual(len(artist_index0_artist1.albums), 1)
        artist_index0_artist_album = artist_index0_artist1.albums[0]
        self.assertEqual(artist_index0_artist_album.id, album1.id)
        self.assertEqual(artist_index0_artist_album.name, album1.name)

        artist_index1 = result.artist_index[1]
        self.assertEqual(artist_index1.name, artist2.name[0])

        self.assertEqual(len(artist_index1.artist), 1)
        artist_index1_artist1 = artist_index1.artist[0]
        self.assertEqual(artist_index1_artist1.id, artist2.id)
        self.assertEqual(artist_index1_artist1.name, artist2.name)

        self.assertEqual(len(artist_index1_artist1.albums), 1)
        artist_index1_artist2_album = artist_index1_artist1.albums[0]
        self.assertEqual(artist_index1_artist2_album.id, album2.id)
        self.assertEqual(artist_index1_artist2_album.name, album2.name)


if __name__ == "__main__":
    unittest.main()
