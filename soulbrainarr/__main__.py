import asyncio

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


if __name__ == "__main__":
    # Get a recommendations list
    number_recommendations: int = 10
    print(f"Getting {number_recommendations} recommendations:")
    recommendations: list[Song] = get_recommendation_list(
        CONFIG.LISTEN_BRAINZ.USERNAME, CONFIG.LISTEN_BRAINZ.EMAIL, number_recommendations=number_recommendations)
    for recommendation in recommendations:
        print(recommendation)

    if CONFIG.BEETS.ENABLE_BEETS:
        print("Skipping already downloaded songs")
        recommendations = remove_already_downloaded_songs(recommendations)
    else:
        print("Beets CONFIG disabled, skipping this step...")

    if len(recommendations) > 0:
        print("Queueing Downloads")
        asyncio.run(search_and_download_recommendations(recommendations))
    else:
        print("No Downloads to Queue.")
