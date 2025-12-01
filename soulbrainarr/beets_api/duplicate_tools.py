from time import time

from beets.library import Library

from soulbrainarr.config_parser import get_config, CONFIG_DATA
from soulbrainarr.song import Song

CONFIG: CONFIG_DATA = get_config()


class ImportedSongsIndex:
    def __init__(self, lib_path: str):
        self.songs: list[Song] = []
        self.title_artist_index: dict[tuple[str, str], Song] = {}
        self.title_list: list[str] = []

        # Load songs from beets library
        lib = Library(lib_path)
        for item in lib.items():
            song = Song(
                item.title,
                item.artist,
                album=item.album,
                beets_file_path=str(item.path)
            )
            self.songs.append(song)

            # Exact-match index (lowercased)
            key = (song.song_title.lower(), song.artist.lower())
            self.title_artist_index[key] = song

            # Keep list of titles for fuzzy search
            self.title_list.append(song.song_title)
        print("Succesfully loaded beets library")

    # -----------------------------
    # Exact lookup
    # -----------------------------
    def has_song_exact(self, song: Song) -> bool:
        key = (song.song_title.lower(), song.artist.lower())
        has_song: bool = key in self.title_artist_index
        if has_song:
            print(f"Exact match found for song {song}")
        return has_song
# -----------------------------
# Remove already downloaded songs
# -----------------------------


def is_song_in_database(song: Song, database: ImportedSongsIndex) -> bool:
    for other_song in database.songs:
        if song == other_song:
            print(f"Fuzzy Match for {song} found with song {other_song}")
            return True

    return False


def skip_already_downloaded_songs(recommendations: list[Song]) -> list[Song]:
    database: ImportedSongsIndex = ImportedSongsIndex(
        CONFIG.BEETS.BEETS_DATABASE)

    new_recs: list[Song] = []
    enable_benchmarking: bool = False

    for rec in recommendations:
        start_time = time()
        has_song: bool = database.has_song_exact(rec)
        if enable_benchmarking:
            print(f"exact check: {time() - start_time}")
        if not has_song:
            start_time = time()
            has_song = is_song_in_database(rec, database)
            if enable_benchmarking:
                print(f"fuzzy check: {time() - start_time}")
            if not has_song:
                new_recs.append(rec)

    return new_recs
