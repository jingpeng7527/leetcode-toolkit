import requests

import config
from review.models import NewProblem, ProblemReview

API = "https://api.notion.com/v1"
VERSION = "2022-06-28"

# Database must have these properties (names and types are exact):
#   Name (title), Slug (rich text), Difficulty (select), Rating (number), Last AC (date),
#   AC Count (number), Overdue Days (number), Lists (multi-select), URL (url)
#   Type (select: Review / New / Daily)
# Optional, filled when a notes page is configured: Notes (url), Topic (select)


def _headers() -> dict:
    if not (config.NOTION_API_KEY and config.NOTION_DATABASE_ID):
        raise RuntimeError("需要在 .env 里设置 NOTION_API_KEY 和 NOTION_DATABASE_ID")
    return {"Authorization": f"Bearer {config.NOTION_API_KEY}", "Notion-Version": VERSION, "Content-Type": "application/json"}


def build_properties(r: ProblemReview, note: dict | None = None) -> dict:
    props = {
        "Name": {"title": [{"text": {"content": r.title}}]},
        "Slug": {"rich_text": [{"text": {"content": r.title_slug}}]},
        "Difficulty": {"select": {"name": r.difficulty}},
        "Last AC": {"date": {"start": r.last_solved.date().isoformat()}},
        "AC Count": {"number": r.times_solved},
        "Overdue Days": {"number": round(r.days_overdue, 1)},
        "Lists": {"multi_select": [{"name": n} for n in r.lists]},
        "URL": {"url": f"https://leetcode.com/problems/{r.title_slug}/"},
        "Type": {"select": {"name": "Review"}},
    }
    if r.rating:
        props["Rating"] = {"number": round(r.rating)}
    if note:
        props["Notes"] = {"url": note["url"]}
        if note["topic"]:
            props["Topic"] = {"select": {"name": note["topic"]}}
    return props


def build_new_properties(p: NewProblem, note: dict | None = None) -> dict:
    """Properties for a problem you haven't solved yet: no Last AC, AC Count or Overdue Days."""
    props = {
        "Name": {"title": [{"text": {"content": p.title}}]},
        "Slug": {"rich_text": [{"text": {"content": p.title_slug}}]},
        "Difficulty": {"select": {"name": p.difficulty}},
        "Lists": {"multi_select": [{"name": n} for n in p.lists]},
        "URL": {"url": f"https://leetcode.com/problems/{p.title_slug}/"},
        "Type": {"select": {"name": p.kind}},
    }
    if p.rating:
        props["Rating"] = {"number": round(p.rating)}
    if note:
        props["Notes"] = {"url": note["url"]}
        if note["topic"]:
            props["Topic"] = {"select": {"name": note["topic"]}}
    return props


def _check_schema(headers: dict) -> None:
    resp = requests.get(f"{API}/databases/{config.NOTION_DATABASE_ID}", headers=headers, timeout=30)
    resp.raise_for_status()
    if "Type" not in resp.json()["properties"]:
        raise RuntimeError("Notion 数据库缺少 Type 列：请添加一个名为 Type 的 Select 列（选项 Review / New / Daily）")


def _find_page(slug: str, headers: dict) -> str | None:
    resp = requests.post(
        f"{API}/databases/{config.NOTION_DATABASE_ID}/query", headers=headers, timeout=30,
        json={"filter": {"property": "Slug", "rich_text": {"equals": slug}}, "page_size": 1},
    )
    resp.raise_for_status()
    results = resp.json()["results"]
    return results[0]["id"] if results else None


def sync_reviews(reviews: list[ProblemReview], notes: dict[str, dict] | None = None,
                 new: list[NewProblem] = ()) -> tuple[int, int]:
    """Upsert one page per problem, matched by Slug. Returns (created, updated)."""
    headers = _headers()
    _check_schema(headers)
    notes = notes or {}
    rows = [(r.title_slug, build_properties(r, notes.get(r.title_slug))) for r in reviews]
    rows += [(p.title_slug, build_new_properties(p, notes.get(p.title_slug))) for p in new]
    created = updated = 0
    for slug, props in rows:
        page_id = _find_page(slug, headers)
        if page_id:
            resp = requests.patch(f"{API}/pages/{page_id}", headers=headers, json={"properties": props}, timeout=30)
            updated += 1
        else:
            resp = requests.post(f"{API}/pages", headers=headers, timeout=30,
                                 json={"parent": {"database_id": config.NOTION_DATABASE_ID}, "properties": props})
            created += 1
        resp.raise_for_status()
    return created, updated
