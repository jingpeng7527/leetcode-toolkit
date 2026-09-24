import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rich.console import Console
from rich.table import Table

from api.client import AuthError, LeetCodeClient
from review.pipeline import load_all, load_new_problems
from review.spaced_repetition import filter_reviews
import config


SHORT = {"NeetCode250": "N250", "NeetCode150": "N150", "Blind75": "B75", "Top100": "T100", "Interview150": "I150"}


def short(name: str) -> str:
    return SHORT.get(name) or name.removeprefix("co:").capitalize()


def main():
    ap = argparse.ArgumentParser(description="按记忆曲线推荐今天该重做的 LeetCode 题")
    ap.add_argument("--all", action="store_true", help="显示所有已做题（含未到期）")
    ap.add_argument("--limit", type=int, default=30, help="最多显示多少题（默认30）")
    ap.add_argument("--new", type=int, default=10, help="额外推荐多少道高频题单里没做过的新题，另加今日每日一题（默认10，0 则不推荐）")
    ap.add_argument("--export", type=Path, help="导出为 csv 文件")
    args = ap.parse_args()

    client = LeetCodeClient()
    console = Console()
    try:
        _, all_reviews, lists = load_all(client, console.status)
        reviews = filter_reviews(all_reviews, config.EXCLUDE_DIFFICULTIES)
        new = load_new_problems(client, all_reviews, lists, args.new) if args.new > 0 else []
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

    if new:
        nt = Table(title=f"新题推荐（每日一题 + 高频题单里没做过的 {sum(p.kind == 'New' for p in new)} 题）")
        for col in ("类型", "题目", "难度", "分数", "所在题单"):
            nt.add_column(col, overflow="fold")
        for p in new:
            nt.add_row("每日" if p.kind == "Daily" else "新题", p.title_slug, p.difficulty,
                       f"{p.rating:.0f}" if p.rating else "-", " ".join(short(n) for n in p.lists) or "-")
        console.print(nt)

    if args.export:
        with args.export.open("w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["type", "slug", "difficulty", "rating", "last_solved", "times_solved", "days_overdue", "lists", "url"])
            for r in shown:
                w.writerow(["review", r.title_slug, r.difficulty, r.rating or "", r.last_solved.date(), r.times_solved,
                            round(r.days_overdue, 1), "|".join(r.lists), f"https://leetcode.com/problems/{r.title_slug}/"])
            for p in new:
                w.writerow([p.kind.lower(), p.title_slug, p.difficulty, p.rating or "", "", "", "", "|".join(p.lists),
                            f"https://leetcode.com/problems/{p.title_slug}/"])
        console.print(f"已导出 {args.export}")


if __name__ == "__main__":
    main()
