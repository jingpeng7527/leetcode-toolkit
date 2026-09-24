import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from review.models import Submission
from review.spaced_repetition import base_interval, compute_reviews, difficulty_factor

NOW = datetime(2026, 9, 23)


def sub(slug, days_ago, ok=True):
    return Submission(slug, slug, NOW - timedelta(days=days_ago), ok)


def test_base_interval_grows_and_extends_past_table():
    assert base_interval(1) == 1 and base_interval(3) == 7
    assert base_interval(8) == 160 * 1.5


def test_high_rating_postponed_and_fallback():
    assert difficulty_factor("Hard", 2100) > difficulty_factor("Hard", 1900)
    assert abs(difficulty_factor("Hard", 2500) - 0.65 * 1.5) < 1e-9
    assert difficulty_factor("Easy", None) == 1.3


def test_failed_submissions_ignored_and_overdue_sign():
    r = compute_reviews([sub("a", 10), sub("b", 10, ok=False)], {"a": "Medium"}, {}, {}, NOW)
    assert [x.title_slug for x in r] == ["a"]
    assert r[0].days_overdue > 0  # interval 1 day, solved 10 days ago
    r = compute_reviews([sub("a", 0)], {"a": "Medium"}, {}, {}, NOW)
    assert r[0].days_overdue < 0


def test_resolving_lengthens_interval():
    once = compute_reviews([sub("a", 5)], {"a": "Medium"}, {}, {}, NOW)[0]
    twice = compute_reviews([sub("a", 20), sub("a", 5)], {"a": "Medium"}, {}, {}, NOW)[0]
    assert twice.interval_days > once.interval_days and twice.times_solved == 2


def test_list_hits_shorten_interval_and_boost_rank():
    subs = [sub("plain", 6), sub("hot", 6)]
    r = compute_reviews(subs, {"plain": "Medium", "hot": "Medium"}, {}, {"hot": ["Top100", "co:google"]}, NOW)
    assert r[0].title_slug == "hot"
    assert r[0].interval_days < r[1].interval_days


def test_filter_reviews_drops_excluded_difficulties():
    from review.spaced_repetition import filter_reviews
    subs = [sub("e", 5), sub("m", 5), sub("h", 5)]
    reviews = compute_reviews(subs, {"e": "Easy", "m": "Medium", "h": "Hard"}, {}, {}, NOW)
    assert {r.title_slug for r in filter_reviews(reviews, {"Easy"})} == {"m", "h"}
    assert len(filter_reviews(reviews, set())) == 3
