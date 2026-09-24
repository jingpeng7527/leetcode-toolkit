import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from integrations.notion import build_properties
from review.models import ProblemReview


def review(**kw):
    base = dict(title_slug="two-sum", title="Two Sum", difficulty="Easy", rating=None, lists=["Top100"],
                last_solved=datetime(2026, 1, 1), times_solved=2, interval_days=3, next_due=datetime(2026, 1, 4), days_overdue=5.0)
    return ProblemReview(**{**base, **kw})


def test_notion_properties():
    p = build_properties(review(rating=1500.4))
    assert p["Rating"] == {"number": 1500} and p["Slug"]["rich_text"][0]["text"]["content"] == "two-sum"
    assert "Rating" not in build_properties(review())


def test_parse_problem_number():
    from integrations.notion_notes import parse_problem_number as p
    assert p("**76. Minimum Window Substring**") == 76
    assert p("非定长 求最大 可不连续缩窗的滑窗-3. Longest Substring Without Repeating Characters") == 3
    assert p("DP - **276. Paint Fence**") == 276
    assert p("变通滑窗 - 1658. Minimum Operations to Reduce X to Zero") == 1658
    assert p("DP思路") is None and p("0-1背包") is None


def test_notion_properties_with_note():
    p = build_properties(review(), {"url": "https://www.notion.so/abc", "topic": "滑动窗口"})
    assert p["Notes"] == {"url": "https://www.notion.so/abc"} and p["Topic"]["select"]["name"] == "滑动窗口"


def test_new_problem_properties_have_type_and_no_review_fields():
    from integrations.notion import build_new_properties
    from review.models import NewProblem
    p = build_new_properties(NewProblem("two-sum", "Two Sum", "Easy", None, ["Top100"], "Daily"))
    assert p["Type"]["select"]["name"] == "Daily" and p["Slug"]["rich_text"][0]["text"]["content"] == "two-sum"
    assert not {"Last AC", "AC Count", "Overdue Days"} & set(p)
    assert build_properties(review())["Type"]["select"]["name"] == "Review"
