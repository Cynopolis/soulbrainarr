import requests
from time import sleep
from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException
from soulbrainarr.song import Song

LB_BASE = "https://api.listenbrainz.org/1"
MB_BASE = "https://musicbrainz.org/ws/2"


def _send_receive(
    url: str,
    *,
    params: dict | None = None,
    headers: dict | None = None,
    timeout: float = 1.0,
    max_retries: int = 3,
):
    """
    Generic GET request wrapper with retries, backoff, and error handling.
    Returns parsed JSON on success, or None on failure.
    """
    sleep_between_attempts_seconds: float = 1
    for attempt in range(1, max_retries + 1):
        try:
            # TODO: Conert this function to use async http library like aiohttp
            resp = requests.get(url, params=params,
                                headers=headers, timeout=timeout)

            # Special handling for 204 (successful but no content)
            if resp.status_code == 204:
                return {"status": 204}

            resp.raise_for_status()
            return resp.json()

        except (ConnectionError, Timeout) as e:
            print(f"[send_receive] Attempt {attempt} connection failure: {e}")
            if attempt < max_retries:
                print(
                    f"[send_receive] Retrying in {sleep_between_attempts_seconds} seconds...")
                sleep(sleep_between_attempts_seconds)
            else:
                print("[send_receive] Max retries reached.")
                return None

        except HTTPError as e:
            status = getattr(e.response, "status_code", None)
            print(f"[send_receive] HTTP error {status}: {e}")

            # Retry only on 5xx
            if status and 500 <= status < 600 and attempt < max_retries:
                print(
                    f"[send_receive] Server error. Retrying in {sleep_between_attempts_seconds} seconds...")
                sleep(sleep_between_attempts_seconds)
            else:
                print("[send_receive] Non-recoverable HTTP error.")
                return None

        except RequestException as e:
            print(f"[send_receive] Unexpected request error: {e}")
            return None

    return None


def _fetch_cf_recommendations(
    username: str,
    header: dict[str, str],
    count: int,
    offset: int = 0,
    timeout: float = 1.0,
    max_retries: int = 3,
):
    """Fetch CF-based recording recommendation MBIDs from ListenBrainz using send_receive()."""

    url = f"{LB_BASE}/cf/recommendation/user/{username}/recording"
    params = {"count": count, "offset": offset}

    # Default return value
    musicbrainz_suggestion_ids: list[str] = []

    data = _send_receive(
        url,
        params=params,
        headers=header,
        timeout=timeout,
        max_retries=max_retries
    )

    if data is None:
        # All errors already logged in send_receive()
        return musicbrainz_suggestion_ids

    if data.get("status") == 204:
        # No recommendations yet
        print("No recommendations generated yet (204).")
        return musicbrainz_suggestion_ids

    # Extract MBIDs if available
    musicbrainz_suggestion_ids = data.get("payload", {}).get("mbids", [])

    return musicbrainz_suggestion_ids


def _resolve_recording_mbid(
    recording_mbid: str,
    header: dict[str, str],
    timeout: float = 1.0,
    max_retries: int = 3,
):
    """
    Given a recording MBID, look up track + artist via MusicBrainz.
    Uses _send_receive() for all network handling.
    """

    url = f"{MB_BASE}/recording/{recording_mbid}"
    params = {"fmt": "json", "inc": "artists"}

    # Default values, ensure single return path
    artist = "Unknown Artist"
    title = "Unknown Title"

    data = _send_receive(
        url,
        params=params,
        headers=header,
        timeout=timeout,
        max_retries=max_retries,
    )

    # If request failed or timed out, return defaults
    if not data or data.get("status") == 204:
        return artist, title

    # Extract title
    title = data.get("title", title)

    # Extract first artist credit
    artist_credits = data.get("artist-credit", [])
    if artist_credits:
        artist = artist_credits[0].get("name", artist)

    return artist, title


def get_recommendation_list(username: str, email: str, number_recommendations: int, recommendation_offset: int = 0) -> list[Song]:
    """
    Get a list of recommendations from ListenBrainz
    """
    headers = {
        "User-Agent": f"LB-Recommendation-Script/1.0 ( {email} )"
    }
    listenbrainz_suggestions_ids = _fetch_cf_recommendations(
        username, headers, number_recommendations, offset=recommendation_offset)
    recommendations: list[Song] = []

    for suggestion in listenbrainz_suggestions_ids:
        mbid: str = suggestion["recording_mbid"]
        score: float = suggestion["score"]
        artist, title = _resolve_recording_mbid(mbid, headers)
        recommendations.append(
            Song(title, artist, score=score, mbid=mbid))

    return recommendations


if __name__ == "__main__":
    from soulbrainarr.config_parser import CONFIG_DATA, get_config
    CONFIG: CONFIG_DATA = get_config()
    recs: list[Song] = get_recommendation_list(
        CONFIG.LISTEN_BRAINZ.USERNAME, CONFIG.LISTEN_BRAINZ.EMAIL, 10)
    for rec in recs:
        print(rec)
