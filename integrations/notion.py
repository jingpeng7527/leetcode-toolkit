import requests

import config
from review.models import ProblemReview

API = "https://api.notion.com/v1"
VERSION = "2022-06-28"

# Database must have these properties (names and types are exact):
#   Name (title), Slug (rich text), Difficulty (select), Rating (number), Last AC (date),
#   AC Count (number), Overdue Days (number), Lists (multi-select), URL (url)
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
    }
    if r.rating:
        props["Rating"] = {"number": round(r.rating)}
    if note:
        props["Notes"] = {"url": note["url"]}
        if note["topic"]:
            props["Topic"] = {"select": {"name": note["topic"]}}
    return props


def _find_page(slug: str, headers: dict) -> str | None:
    resp = requests.post(
        f"{API}/databases/{config.NOTION_DATABASE_ID}/query", headers=headers, timeout=30,
        json={"filter": {"property": "Slug", "rich_text": {"equals": slug}}, "page_size": 1},
    )
    resp.raise_for_status()
    results = resp.json()["results"]
    return results[0]["id"] if results else None


def sync_reviews(reviews: list[ProblemReview], notes: dict[str, dict] | None = None) -> tuple[int, int]:
    """Upsert one page per problem, matched by Slug. Returns (created, updated)."""
    headers = _headers()
    created = updated = 0
    for r in reviews:
        props = build_properties(r, (notes or {}).get(r.title_slug))
        page_id = _find_page(r.title_slug, headers)
        if page_id:
            resp = requests.patch(f"{API}/pages/{page_id}", headers=headers, json={"properties": props}, timeout=30)
            updated += 1
        else:
            resp = requests.post(f"{API}/pages", headers=headers, timeout=30,
                                 json={"parent": {"database_id": config.NOTION_DATABASE_ID}, "properties": props})
            created += 1
        resp.raise_for_status()
    return created, updated
