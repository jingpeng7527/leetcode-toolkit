"""Synthetic review records for the public demo page. Nothing here comes from a real account:
problems are sampled from public lists and every date, count and note is random."""
import random
from datetime import datetime, timedelta

from review.models import Submission
from review.spaced_repetition import compute_reviews

TOPICS = ["滑动窗口", "双指针", "DP", "图", "BFS", "栈", "链表", "二分查找"]


def title_from_slug(slug: str) -> str:
    return " ".join(w.capitalize() for w in slug.split("-"))


def make_demo(lists_by_slug: dict[str, list[str]], difficulties: dict[str, str], ratings: dict[str, float],
              today: datetime, n: int = 120, seed: int = 7):
    """Returns (submissions, notes) to feed into the normal review pipeline."""
    rng = random.Random(seed)
    slugs = sorted(lists_by_slug)
    rng.shuffle(slugs)
    subs, notes = [], {}
    for slug in slugs[:n]:
        times = rng.choices([1, 2, 3, 4], weights=[5, 3, 2, 1])[0]
        last_days = rng.choice([rng.randint(1, 6), rng.randint(1, 30), rng.randint(30, 200), rng.randint(200, 900)])
        gaps = sorted(rng.randint(last_days, last_days + 500) for _ in range(times - 1))
        for days_ago in [last_days] + gaps:
            subs.append(Submission(slug, title_from_slug(slug), today - timedelta(days=days_ago, hours=rng.randint(0, 20)), True))
        if rng.random() < 0.3:
            notes[slug] = {"url": None, "topic": rng.choice(TOPICS)}
    return subs, notes


def make_daily(today: datetime, seed: int = 11) -> dict[str, int]:
    """Random per-day AC counts for the last year, with streaks and quiet weeks."""
    rng = random.Random(seed)
    out, active = {}, False
    for i in range(371, -1, -1):
        day = (today - timedelta(days=i)).date()
        active = rng.random() < (0.8 if active else 0.25)
        if active:
            out[day.isoformat()] = rng.choice([1, 1, 2, 2, 3, 4, 6])
    return out
