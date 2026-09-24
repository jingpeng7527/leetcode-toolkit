import requests

from api.cache import cached_json

RATING_URL = "https://zerotrac.github.io/leetcode_problem_rating/data.json"


def load_ratings() -> dict[str, float]:
    """titleSlug -> contest-derived rating (only problems that appeared in contests)."""
    def fetch():
        resp = requests.get(RATING_URL, timeout=30)
        resp.raise_for_status()
        return {p["TitleSlug"]: p["Rating"] for p in resp.json()}
    return cached_json("ratings", fetch)
