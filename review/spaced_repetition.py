from datetime import datetime, timedelta

from review.models import ProblemReview, Submission

BASE_INTERVALS = [1, 3, 7, 16, 35, 75, 160]
TAIL_GROWTH = 1.5
FALLBACK_FACTOR = {"Easy": 1.3, "Medium": 1.0, "Hard": 0.7}
HIGH_RATING = 2000
HIGH_RATING_POSTPONE = 1.5
HIT_INTERVAL_SHRINK = 0.1  # interval *= 1 / (1 + 0.1 * hits)
HIT_PRIORITY_WEIGHT = 0.25  # priority = forget_prob * (1 + 0.25 * hits)


def base_interval(times_solved: int) -> float:
    if times_solved <= len(BASE_INTERVALS):
        return BASE_INTERVALS[times_solved - 1]
    return BASE_INTERVALS[-1] * TAIL_GROWTH ** (times_solved - len(BASE_INTERVALS))


def difficulty_factor(difficulty: str, rating: float | None) -> float:
    if rating is None:
        return FALLBACK_FACTOR.get(difficulty, 1.0)
    factor = min(1.3, max(0.6, 1.3 - (rating - 1200) / 2000))
    if rating > HIGH_RATING:
        factor *= HIGH_RATING_POSTPONE
    return factor


def forget_probability(last: datetime, interval_days: float, today: datetime) -> float:
    """1 - retention, with retention halving every interval_days. Saturates near 1 for long-forgotten problems,
    so among those, list/company hits decide the order rather than raw age."""
    elapsed = max(0.0, (today - last).total_seconds() / 86400)
    return 1 - 0.5 ** (elapsed / interval_days)


def compute_reviews(
    submissions: list[Submission],
    difficulties: dict[str, str],
    ratings: dict[str, float],
    lists_by_slug: dict[str, list[str]],
    today: datetime | None = None,
) -> list[ProblemReview]:
    """One ProblemReview per solved problem, most urgent first. days_overdue >= 0 means due."""
    today = today or datetime.now()
    solved: dict[str, list[Submission]] = {}
    for s in submissions:
        if s.accepted:
            solved.setdefault(s.title_slug, []).append(s)

    reviews = []
    for slug, subs in solved.items():
        subs.sort(key=lambda s: s.timestamp)
        difficulty = difficulties.get(slug, "Medium")
        rating = ratings.get(slug)
        hits = lists_by_slug.get(slug, [])
        interval = base_interval(len(subs)) * difficulty_factor(difficulty, rating) / (1 + HIT_INTERVAL_SHRINK * len(hits))
        last = subs[-1].timestamp
        next_due = last + timedelta(days=interval)
        overdue = (today - next_due).total_seconds() / 86400
        reviews.append(ProblemReview(
            title_slug=slug, title=subs[-1].title, difficulty=difficulty, rating=rating, lists=list(hits),
            last_solved=last, times_solved=len(subs), interval_days=interval, next_due=next_due,
            days_overdue=overdue, priority=forget_probability(last, interval, today) * (1 + HIT_PRIORITY_WEIGHT * len(hits)),
        ))
    reviews.sort(key=lambda r: (r.priority, r.days_overdue), reverse=True)
    return reviews
