import asyncio
from time import sleep
import os

from soulbrainarr.song import Song

from .config_parser import get_config, CONFIG_DATA
from .listen_brainz_api import get_recommendation_list
from .slskd_api import search_slskd, attempt_each_download
from .file_check.song_checker import remove_already_downloaded_songs

CONFIG: CONFIG_DATA = get_config()


async def search_and_download(rec: Song):
    search_term: str = f"{rec.artist} {rec.song_title}"
    print(f"Searching for: {search_term}")
    search_responses = await search_slskd(search_term)

    if attempt_each_download(search_responses):
        print(f"Download for {search_term} succeeded")
    else:
        print(f"Download for {search_term} failed")


async def search_and_download_recommendations(recs: list[Song]):
    # search recommendations in slskd_api
    await asyncio.gather(*[search_and_download(rec) for rec in recs])


async def main(song_batch_size: int, song_rec_offset: int):
    print("================================")

    print(
        f"Getting {song_batch_size} recommendations with offset {song_rec_offset}:")
    recommendations: list[Song] = get_recommendation_list(
        CONFIG.LISTEN_BRAINZ.USERNAME,
        CONFIG.LISTEN_BRAINZ.EMAIL,
        song_batch_size,
        recommendation_offset=song_rec_offset
    )

    # List all of the recommendations in the logs
    for recommendation in recommendations:
        print(recommendation)

    if CONFIG.BEETS.ENABLE_BEETS:
        print("Skipping already downloaded songs")
        recommendations = remove_already_downloaded_songs(recommendations)
    else:
        print("Beets CONFIG disabled, skipping this step...")

    if len(recommendations) > 0:
        print("Queueing Downloads")
        await search_and_download_recommendations(recommendations)
    else:
        print("No Downloads to Queue.")
    print("================================")


async def looper():
    run_interval_seconds: int = CONFIG.SOULBRAINARR.RUN_INTERVAL_MINUTES * 60
    song_offset: int = 0
    while True:
        await main(CONFIG.SOULBRAINARR.SONG_BATCH_SIZE, song_offset)
        song_offset += CONFIG.SOULBRAINARR.SONG_BATCH_SIZE
        print(
            f"Sleeping for {CONFIG.SOULBRAINARR.RUN_INTERVAL_MINUTES} minutes")
        sleep(run_interval_seconds)

if __name__ == "__main__":
    asyncio.run(looper())
