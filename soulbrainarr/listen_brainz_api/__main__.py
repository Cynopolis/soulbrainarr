import requests
from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException
from soulbrainarr.song import Song

LB_BASE = "https://api.listenbrainz.org/1"
MB_BASE = "https://musicbrainz.org/ws/2"


def _fetch_cf_recommendations(
    username: str,
    header: dict[str, str],
    count: int = 20,
    offset: int = 0,
    timeout: float = 1.0,
    max_retries: int = 3,
    backoff_factor: float = 0.5
):
    """Fetch CF-based recording recommendation mbids from ListenBrainz with error handling."""
    url = f"{LB_BASE}/cf/recommendation/user/{username}/recording"
    params = {"count": count, "offset": offset}

    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.get(url, params=params,
                                headers=header, timeout=timeout)

            if resp.status_code == 204:
                print("No recommendations generated yet (204).")
                return []

            resp.raise_for_status()
            data = resp.json()
            musicbrainz_suggestion_ids = data.get(
                "payload", {}).get("mbids", [])
            return musicbrainz_suggestion_ids

        except (ConnectionError, Timeout) as e:
            print(f"Attempt {attempt} failed: {e}")
            if attempt == max_retries:
                print("Max retries reached. Returning empty list.")
                return []
            sleep_time = backoff_factor * (2 ** (attempt - 1))
            print(f"Retrying in {sleep_time:.1f} seconds...")
            time.sleep(sleep_time)

        except HTTPError as e:
            status = getattr(e.response, "status_code", "unknown")
            print(f"HTTP error {status}: {e}")
            if 500 <= status < 600 and attempt < max_retries:
                sleep_time = backoff_factor * (2 ** (attempt - 1))
                print(f"Server error. Retrying in {sleep_time:.1f} seconds...")
                time.sleep(sleep_time)
            else:
                return []

        except RequestException as e:
            print(f"Unexpected request error: {e}")
            return []

    return []


def _resolve_recording_mbid(recording_mbid: str, header: dict[str, str], timeout: float = 1.0):
    """
    Given a recording MBID, look up the track + artist using MusicBrainz.
    """
    url = f"{MB_BASE}/recording/{recording_mbid}"
    params = {"fmt": "json", "inc": "artists"}
    # TODO: Add timeout exception and connection reset by peer exceptions to this
    resp = requests.get(url, params=params, headers=header, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()

    title = data.get("title", "Unknown Title")

    # Extract the first listed artist
    artist_credits = data.get("artist-credit", [])
    if artist_credits:
        artist = artist_credits[0].get("name", "Unknown Artist")
    else:
        artist = "Unknown Artist"

    return artist, title


def get_recommendation_list(username: str, email: str, number_recommendations: int = 10) -> list[Song]:
    """
    Get a list of recommendations from ListenBrainz
    """
    headers = {
        "User-Agent": f"LB-Recommendation-Script/1.0 ( {email} )"
    }
    # TODO: Handle exceptions
    listenbrainz_suggestions_ids = _fetch_cf_recommendations(
        username, headers, count=number_recommendations)
    recommendations: list[Song] = []

    for suggestion in listenbrainz_suggestions_ids:
        mbid: str = suggestion["recording_mbid"]
        score: float = suggestion["score"]
        # TODO: Handle exceptions
        artist, title = _resolve_recording_mbid(mbid, headers)
        recommendations.append(
            Song(title, artist, score=score, mbid=mbid))

    return recommendations


if __name__ == "__main__":
    print(get_recommendation_list("UsernameHere", "example@gmail.com"))
