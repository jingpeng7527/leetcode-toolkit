import re

import requests

import config
from api.cache import cached_json
from api.client import LeetCodeClient
from integrations.notion import API, VERSION

# A note page title contains "<number>. <problem name>", e.g. "滑动窗口 - 3. Longest Substring ..."
NUMBER_RE = re.compile(r"(?<!\d)(\d{1,4})\.\s+[A-Za-z]")


def parse_problem_number(title: str) -> int | None:
    m = NUMBER_RE.search(title.replace("*", ""))
    return int(m.group(1)) if m else None


def _headers() -> dict:
    return {"Authorization": f"Bearer {config.NOTION_API_KEY}", "Notion-Version": VERSION}


def _children(block_id: str) -> list[dict]:
    out, cursor = [], None
    while True:
        params = {"page_size": 100, **({"start_cursor": cursor} if cursor else {})}
        resp = requests.get(f"{API}/blocks/{block_id}/children", headers=_headers(), params=params, timeout=30)
        if resp.status_code == 404:
            raise RuntimeError("Notion integration 读不到笔记页面：请在该页面 ••• → Connections 里添加你的 integration")
        resp.raise_for_status()
        body = resp.json()
        out.extend(body["results"])
        if not body["has_more"]:
            return out
        cursor = body["next_cursor"]


def _child_pages(block_id: str) -> list[dict]:
    """Child pages of a block, looking inside toggles/columns too (but not inside child pages)."""
    pages = []
    for b in _children(block_id):
        if b["type"] == "child_page":
            pages.append({"id": b["id"], "title": b["child_page"]["title"]})
        elif b.get("has_children"):
            pages.extend(_child_pages(b["id"]))
    return pages


def crawl_notes(root_page_id: str) -> list[dict]:
    """[{number, title, topic, url}] for every problem note page one or two levels under the root."""
    found = []
    for top in _child_pages(root_page_id):
        candidates = [(top, "")]
        candidates += [(p, top["title"]) for p in _child_pages(top["id"])]
        for page, topic in candidates:
            number = parse_problem_number(page["title"])
            if number:
                found.append({"number": number, "title": page["title"], "topic": topic,
                              "url": f"https://www.notion.so/{page['id'].replace('-', '')}"})
    return found


def load_notes(client: LeetCodeClient) -> dict[str, dict]:
    """titleSlug -> {url, topic}. Empty if NOTION_NOTES_PAGE_ID is not configured."""
    if not config.NOTION_NOTES_PAGE_ID:
        return {}
    notes = cached_json("notion_notes", lambda: crawl_notes(config.NOTION_NOTES_PAGE_ID), max_age_hours=1)
    by_number = cached_json("slugs_by_number", lambda: {str(k): v for k, v in client.slugs_by_number().items()}, max_age_hours=168)
    out: dict[str, dict] = {}
    for n in notes:
        slug = by_number.get(str(n["number"]))
        if slug and slug not in out:
            out[slug] = {"url": n["url"], "topic": n["topic"]}
    return out
