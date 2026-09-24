import argparse
import json
import sys
import webbrowser
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rich.console import Console

import config
from api.client import AuthError, LeetCodeClient
from review.pipeline import load_all

TEMPLATE = Path(__file__).with_name("dashboard_template.html")
LIST_LABELS = {"NeetCode250": "NeetCode 250", "NeetCode150": "NeetCode 150", "Blind75": "Blind 75",
               "Top100": "LeetCode Top 100", "Interview150": "Interview 150"}


def label(name: str) -> str:
    return LIST_LABELS.get(name) or name.removeprefix("co:").capitalize()


def build_data(subs, reviews, lists, notes, today: datetime) -> dict:
    problems = []
    for i, r in enumerate(reviews):
        elapsed = max(0.0, (today - r.last_solved).total_seconds() / 86400)
        note = notes.get(r.title_slug)
        problems.append({
            "rank": i + 1, "slug": r.title_slug, "title": r.title, "difficulty": r.difficulty,
            "rating": round(r.rating) if r.rating else None, "lists": [label(n) for n in r.lists],
            "last": r.last_solved.strftime("%Y-%m-%d"), "times": r.times_solved,
            "interval": round(r.interval_days, 2), "elapsed": round(elapsed, 1),
            "retention": round(0.5 ** (elapsed / r.interval_days), 4),
            "note": note["url"] if note else None, "topic": note["topic"] if note else None,
        })
    by_slug = {p["slug"]: p for p in problems}

    coverage = []
    for name, slugs in lists.items():
        fresh = due = 0
        missing = []
        for s in slugs:
            p = by_slug.get(s)
            if p is None:
                missing.append(s)
            elif p["retention"] > 0.5:
                fresh += 1
            else:
                due += 1
        coverage.append({"name": label(name), "total": len(slugs), "fresh": fresh, "due": due,
                         "missing": len(missing), "missing_slugs": missing[:40]})

    start = today.date() - timedelta(days=370)
    daily = Counter(s.timestamp.date().isoformat() for s in subs if s.accepted and s.timestamp.date() >= start)
    return {
        "today": today.strftime("%Y-%m-%d"), "problems": problems, "coverage": coverage, "daily": daily,
        "notes_total": len(notes),
    }


def main():
    ap = argparse.ArgumentParser(description="生成本地复习仪表盘 dashboard.html")
    ap.add_argument("--out", type=Path, default=Path("dashboard.html"))
    ap.add_argument("--no-open", action="store_true")
    args = ap.parse_args()

    console = Console()
    client = LeetCodeClient()
    try:
        subs, reviews, lists = load_all(client, console.status)
    except AuthError as e:
        sys.exit(f"错误：{e}")
    notes = {}
    if config.NOTION_NOTES_PAGE_ID and config.NOTION_API_KEY:
        try:
            from integrations.notion_notes import load_notes
            with console.status("读取 Notion 笔记..."):
                notes = load_notes(client)
        except Exception as e:
            console.print(f"[yellow]跳过笔记关联：{e}[/yellow]")

    data = build_data(subs, reviews, lists, notes, datetime.now())
    html = TEMPLATE.read_text().replace("__DATA__", json.dumps(data, ensure_ascii=False).replace("</", "<\\/"))
    args.out.write_text(html)
    console.print(f"已生成 {args.out.resolve()}")
    if not args.no_open:
        webbrowser.open(args.out.resolve().as_uri())


if __name__ == "__main__":
    main()
