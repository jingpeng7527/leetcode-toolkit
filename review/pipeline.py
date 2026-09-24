from datetime import datetime

import config
from api.cache import cached_json
from api.client import LeetCodeClient
from api.lists import hits_by_slug, load_lists
from api.rating import load_ratings
from review.models import NewProblem, ProblemReview, Submission
from review.new_problems import pick_new_problems
from review.spaced_repetition import compute_reviews, filter_reviews


def _problemset(client: LeetCodeClient) -> dict[str, dict]:
    """slug -> {title, difficulty, ...} for every problem, cached for a day."""
    return {q["titleSlug"]: q for q in cached_json("problemset", client.problemset)}


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
        difficulties = {slug: q["difficulty"] for slug, q in _problemset(client).items()}
        ratings = load_ratings()
        lists = load_lists(client)
    return subs, compute_reviews(subs, difficulties, ratings, hits_by_slug(lists)), lists


def load_reviews(client: LeetCodeClient, status=None) -> list[ProblemReview]:
    """Ranked review queue, without the difficulties listed in EXCLUDE_DIFFICULTIES (default Easy)."""
    return filter_reviews(load_all(client, status)[1], config.EXCLUDE_DIFFICULTIES)


def load_new_problems(client: LeetCodeClient, reviews: list[ProblemReview], lists: dict[str, list[str]], n: int) -> list[NewProblem]:
    """Daily challenge plus the top n unsolved list problems. `reviews` must be the unfiltered set, so
    problems you solved (whatever their difficulty) are never suggested again."""
    try:
        d = client.daily_challenge()
        daily = {"slug": d["question"]["titleSlug"], "title": d["question"]["title"], "difficulty": d["question"]["difficulty"]}
    except Exception:  # the daily challenge is a nicety; never let it break the queue
        daily = None
    return pick_new_problems(lists, {r.title_slug for r in reviews}, _problemset(client), load_ratings(),
                             config.EXCLUDE_DIFFICULTIES, n, daily)


class _Noop:
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False
