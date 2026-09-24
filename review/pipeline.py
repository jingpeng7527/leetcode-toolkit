from datetime import datetime

from api.client import LeetCodeClient
from api.lists import hits_by_slug, load_lists
from api.rating import load_ratings
from review.models import ProblemReview, Submission
from review.spaced_repetition import compute_reviews


def load_all(client: LeetCodeClient, status=None):
    """Fetch everything once. Returns (submissions, ranked reviews, lists by name)."""
    def step(msg):
        return status(msg) if status else _Noop()

    with step("拉取提交历史..."):
        raw = client.all_submissions()
    subs = [
        Submission(r["titleSlug"], r["title"], datetime.fromtimestamp(int(r["timestamp"])), r["statusDisplay"] == "Accepted")
        for r in raw
    ]
    with step("拉取难度/题单..."):
        difficulties = client.difficulties()
        ratings = load_ratings()
        lists = load_lists(client)
    return subs, compute_reviews(subs, difficulties, ratings, hits_by_slug(lists)), lists


def load_reviews(client: LeetCodeClient, status=None) -> list[ProblemReview]:
    return load_all(client, status)[1]


class _Noop:
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False
