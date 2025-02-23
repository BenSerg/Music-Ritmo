from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Sequence

from src.app.dto import *


def add_if_not_none(rsp: Dict[str, Any], attr: str, val: Any) -> None:
    if val is not None:
        rsp[attr] = val


def add_str_if_not_empty(rsp: Dict[str, Any], attr: str, val: str) -> None:
    if val != "":
        rsp[attr] = val


def add_str_or_default(rsp: Dict[str, Any], attr: str, s: str | None) -> None:
    if s is not None:
        rsp[attr] = s
    else:
        rsp[attr] = ""


def add_int_or_default(rsp: Dict[str, Any], attr: str, i: int | None) -> None:
    if i is not None:
        rsp[attr] = i
    else:
        rsp[attr] = 0


def add_list_if_not_empty(rsp: Dict[str, Any], attr: str, l: List[Any]) -> None:
    if len(l) > 0:
        rsp[attr] = l


def add_datetime_if_not_none(
    rsp: Dict[str, Any], attr: str, dt: datetime | None
) -> None:
    if dt is not None:
        rsp[attr] = dt.isoformat()


class OpenSubsonicFormatter:
    @staticmethod
    def format_genre(genre: Genre) -> dict[str, Any]:
        return {
            "albumCount": genre.albumCount,
            "songCount": genre.songCount,
            "value": genre.name,
        }

    @staticmethod
    def format_genres(genres: Sequence[Genre]) -> dict[str, Any]:
        return {"genre": list(map(OpenSubsonicFormatter.format_genre, genres))}

    @staticmethod
    def format_genre_item(genre_item: GenreItem) -> dict[str, Any]:
        return {"name": genre_item.name}

    @staticmethod
    def format_artist_item(artist_item: ArtistItem) -> dict[str, Any]:
        result = {"id": artist_item.id, "name": artist_item.name}

        add_if_not_none(result, "albumCount", artist_item.album_count)
        add_if_not_none(result, "coverArt", artist_item.cover_art_id)
        add_datetime_if_not_none(result, "coverArt", artist_item.starred)

        return result

    @staticmethod
    def format_track(track: Track) -> dict[str, Any]:
        result = {"id": track.id, "isDir": False, "title": track.title, "type": "music"}

        add_if_not_none(result, "ablum", track.album)
        add_if_not_none(result, "ablumId", track.album_id)
        add_if_not_none(result, "parent", track.album_id)

        add_if_not_none(result, "artist", track.artist)
        add_if_not_none(result, "artistId", track.artist_id)

        add_if_not_none(result, "track", track.track_number)
        add_if_not_none(result, "discNumber", track.disc_number)
        add_if_not_none(result, "year", track.year)
        add_if_not_none(result, "genre", track.genre)

        add_int_or_default(result, "bpm", track.bpm)
        add_str_or_default(result, "comment", track.comment)

        add_if_not_none(
            result,
            "coverArt",
            f"mf-{track.cover_art_id}" if track.cover_art_id else None,
        )

        if track.path is not None:
            add_str_if_not_empty(result, "path", track.path)
            add_str_if_not_empty(result, "suffix", Path(track.path).suffix)

        add_if_not_none(result, "size", track.file_size)
        add_if_not_none(result, "contentType", track.content_type)
        add_if_not_none(result, "duration", track.duration)
        add_if_not_none(result, "bitRate", track.bit_rate)
        add_if_not_none(result, "bitDepth", track.bit_depth)
        add_if_not_none(result, "samplingRate", track.sampling_rate)
        add_if_not_none(result, "channelCount", track.channel_count)

        add_if_not_none(result, "playCount", track.play_count)

        add_datetime_if_not_none(result, "created", track.created)
        add_datetime_if_not_none(result, "starred", track.starred)

        result["artists"] = list(
            map(OpenSubsonicFormatter.format_artist_item, track.artists)
        )
        result["genres"] = list(
            map(OpenSubsonicFormatter.format_genre_item, track.genres)
        )

        return result

    @staticmethod
    def format_tracks(tracks: Sequence[Track]) -> dict[str, Any]:
        return {"song": list(map(OpenSubsonicFormatter.format_track, tracks))}
