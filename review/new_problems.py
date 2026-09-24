from api.lists import hits_by_slug
from review.models import NewProblem
from review.spaced_repetition import HIGH_RATING

UNKNOWN_RATING = 1400  # problems without a contest rating sort as mid-difficulty


def pick_new_problems(
    lists: dict[str, list[str]],
    solved: set[str],
    problemset: dict[str, dict],
    ratings: dict[str, float],
    exclude_difficulties: set[str],
    n: int,
    daily: dict | None = None,
) -> list[NewProblem]:
    """Today's daily challenge (if unsolved), then up to n unsolved problems that appear in the most lists.

    Ties are broken by lower rating first, so easier problems come before harder ones. Problems rated above
    HIGH_RATING go last, like in the review queue. Problems of an excluded difficulty are skipped; the
    daily challenge is always offered.
    """
    picks: list[NewProblem] = []
    hits = hits_by_slug(lists)
    daily_slug = daily["slug"] if daily else None
    if daily and daily_slug not in solved:
        picks.append(NewProblem(daily_slug, daily["title"], daily["difficulty"], ratings.get(daily_slug),
                                hits.get(daily_slug, []), "Daily"))

    candidates = [
        s for s in hits
        if s not in solved and s != daily_slug and s in problemset
        and problemset[s]["difficulty"] not in exclude_difficulties
    ]
    candidates.sort(key=lambda s: (ratings.get(s, 0) > HIGH_RATING, -len(hits[s]), ratings.get(s, UNKNOWN_RATING), s))
    for s in candidates[:n]:
        picks.append(NewProblem(s, problemset[s]["title"], problemset[s]["difficulty"], ratings.get(s), hits[s], "New"))
    return picks
