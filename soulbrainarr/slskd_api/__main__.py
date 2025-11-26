import asyncio
import json

from requests.exceptions import HTTPError

import slskd_api
from slskd_api.apis._types import SearchResponseItem
from soulbrainarr.config_parser import get_config, CONFIG_DATA
from .log_parser import parse_log_to_exception

CONFIG: CONFIG_DATA = get_config()

SLSKD = slskd_api.SlskdClient(
    host=CONFIG.SLSKD.HOST,
    api_key=CONFIG.SLSKD.API_KEY
)


def _print_formatted_dict(dictionary: dict):
    print(json.dumps(dictionary, indent=2))


async def search_slskd(search_text: str) -> list[SearchResponseItem]:
    """
    Have a slskd instance search soulseek for something
    """

    # TODO: Check if we've done this search in the last day
    # searches = slskd.searches.get_all()

    # TODO: Do some search text validation
    test_search_id = SLSKD.searches.search_text(search_text)["id"]

    # Wait for the search to be done
    while not SLSKD.searches.state(test_search_id)["isComplete"]:
        await asyncio.sleep(0.1)

    search_responses = SLSKD.searches.search_responses(test_search_id)

    return search_responses


def attempt_download(search_response: SearchResponseItem) -> bool:
    '''
    This will attempt to enqueue all of the search response items given to it
    '''
    username = search_response["username"]
    files = search_response["files"]
    success: bool = False
    try:
        if SLSKD.transfers.enqueue(username, files):
            success = True
    except HTTPError as e:
        print(e)

    # Check the download result
    log = SLSKD.logs.get()[-1]
    error = parse_log_to_exception(log)
    if error is not None:
        print(error)
        success = False
    return success


def attempt_each_download(search_responses: list[SearchResponseItem]) -> bool:
    '''
    This will individually attempt to download each of the given search response items until one succeeds
    '''
    success: bool = False
    for response in search_responses:
        if attempt_download(response):
            success = True
            break

    return success


async def main():
    # print("Starting test")
    # SEARCH_RESULTS = await search_slskd("Bondgirl Scary Goldings")
    # print(json.dumps(SEARCH_RESULTS, indent=2))
    from .example_search import SEARCH_RESULTS
    if attempt_each_download(SEARCH_RESULTS):
        print("Download succeeded")
    else:
        print("Download Failed")


if __name__ == "__main__":
    asyncio.run(main())
