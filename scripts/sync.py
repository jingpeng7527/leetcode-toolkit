import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rich.console import Console

from api.client import AuthError, LeetCodeClient
from review.pipeline import load_reviews


def main():
    ap = argparse.ArgumentParser(description="把复习列表同步到 Notion")
    ap.add_argument("--target", choices=["notion"], default="notion")
    ap.add_argument("--limit", type=int, default=50, help="同步最优先的前 N 题（默认50）")
    ap.add_argument("--all", action="store_true", help="包含未到期的题")
    args = ap.parse_args()

    console = Console()
    try:
        client = LeetCodeClient()
        reviews = load_reviews(client, console.status)
    except AuthError as e:
        sys.exit(f"错误：{e}")
    if not args.all:
        reviews = [r for r in reviews if r.days_overdue >= 0]
    top = reviews[: args.limit]

    from integrations.notion import sync_reviews
    from integrations.notion_notes import load_notes
    try:
        notes = load_notes(client)
    except RuntimeError as e:
        sys.exit(f"错误：{e}")
    # Always include problems you wrote notes for, even outside the top N, so the link is never missing.
    reviews = top + [r for r in reviews[args.limit:] if r.title_slug in notes]
    created, updated = sync_reviews(reviews, notes)
    matched = sum(1 for r in reviews if r.title_slug in notes)
    console.print(f"Notion：新建 {created}，更新 {updated}；其中 {matched} 题关联了笔记（共发现 {len(notes)} 篇笔记）")


if __name__ == "__main__":
    main()
