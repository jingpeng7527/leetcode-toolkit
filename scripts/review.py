import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rich.console import Console
from rich.table import Table

from api.client import AuthError, LeetCodeClient
from review.pipeline import load_reviews


SHORT = {"NeetCode250": "N250", "NeetCode150": "N150", "Blind75": "B75", "Top100": "T100", "Interview150": "I150"}


def short(name: str) -> str:
    return SHORT.get(name) or name.removeprefix("co:").capitalize()


def main():
    ap = argparse.ArgumentParser(description="按记忆曲线推荐今天该重做的 LeetCode 题")
    ap.add_argument("--all", action="store_true", help="显示所有已做题（含未到期）")
    ap.add_argument("--limit", type=int, default=30, help="最多显示多少题（默认30）")
    ap.add_argument("--export", type=Path, help="导出为 csv 文件")
    args = ap.parse_args()

    client = LeetCodeClient()
    console = Console()
    try:
        reviews = load_reviews(client, console.status)
    except AuthError as e:
        sys.exit(f"错误：{e}")
    shown = reviews if args.all else [r for r in reviews if r.days_overdue >= 0]

    table = Table(title=f"今日复习推荐（共 {len(shown)} 题，显示前 {min(len(shown), args.limit)}）")
    for col in ("题目", "难度", "分数", "上次AC", "AC次数", "超期(天)", "所在题单"):
        table.add_column(col, overflow="fold")
    for r in shown[: args.limit]:
        table.add_row(
            r.title_slug, r.difficulty, f"{r.rating:.0f}" if r.rating else "-", r.last_solved.strftime("%Y-%m-%d"),
            str(r.times_solved), f"{r.days_overdue:.1f}", " ".join(short(n) for n in r.lists) or "-",
        )
    console.print(table)

    if args.export:
        with args.export.open("w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["slug", "difficulty", "rating", "last_solved", "times_solved", "days_overdue", "lists", "url"])
            for r in shown:
                w.writerow([r.title_slug, r.difficulty, r.rating or "", r.last_solved.date(), r.times_solved,
                            round(r.days_overdue, 1), "|".join(r.lists), f"https://leetcode.com/problems/{r.title_slug}/"])
        console.print(f"已导出 {args.export}")


if __name__ == "__main__":
    main()
