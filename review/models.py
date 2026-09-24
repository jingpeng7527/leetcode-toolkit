from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Submission:
    title_slug: str
    title: str
    timestamp: datetime
    accepted: bool


@dataclass
class ProblemReview:
    title_slug: str
    title: str
    difficulty: str
    rating: float | None
    lists: list[str] = field(default_factory=list)
    last_solved: datetime | None = None
    times_solved: int = 0
    interval_days: float = 0.0
    next_due: datetime | None = None
    days_overdue: float = 0.0
    priority: float = 0.0


@dataclass
class NewProblem:
    """A problem worth starting: today's daily challenge or an unsolved problem from the interview lists."""
    title_slug: str
    title: str
    difficulty: str
    rating: float | None
    lists: list[str] = field(default_factory=list)
    kind: str = "New"  # "New" or "Daily"
