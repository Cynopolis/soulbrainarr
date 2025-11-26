from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from rapidfuzz import fuzz

from slskd_api.apis._types import SearchResponseItem


@dataclass
class Song:
    song_title: str
    artist: str
    score: Optional[float] = None
    album: Optional[str] = None
    beets_file_path: Optional[str] = None
    mbid: Optional[str] = None

    def __str__(self) -> str:
        return f"{self.song_title} by {self.artist}"

    def __eq__(self, other: Song) -> bool:
        FUZZY_THRESHOLD_TITLE: float = 0.8
        FUZZY_THRESHOLD_ARTIST: float = 0.8
        FUZZY_THRESHOLD_ALBUM: float = 0.8

        # --- Title Match ---
        if self.song_title and other.song_title:
            exact_title = self.song_title == other.song_title
            fuzzy_title = (
                fuzz.token_sort_ratio(self.song_title, other.song_title)
                >= FUZZY_THRESHOLD_TITLE
            )
            song_title_is_same = exact_title or fuzzy_title
        else:
            song_title_is_same = False

        # --- Artist Match ---
        if self.artist and other.artist:
            exact_artist = self.artist == other.artist
            fuzzy_artist = (
                fuzz.token_sort_ratio(self.artist, other.artist)
                >= FUZZY_THRESHOLD_ARTIST
            )
            artist_is_same = exact_artist or fuzzy_artist
        else:
            artist_is_same = False

        # --- Album Match (Optional) ---
        if self.album and other.album:
            exact_album = self.album == other.album
            fuzzy_album = (
                fuzz.token_sort_ratio(self.album, other.album)
                >= FUZZY_THRESHOLD_ALBUM
            )
            album_is_same = exact_album or fuzzy_album
        else:
            # If either album is None, default to your original "ignore album" logic
            album_is_same = True

        return song_title_is_same and artist_is_same and album_is_same
