import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from integrations.claude import explain_problem


def main():
    ap = argparse.ArgumentParser(description="用 Claude 讲解一道题（分层提示，不直接给代码）")
    ap.add_argument("slug", help="题目 titleSlug，如 two-sum")
    ap.add_argument("--language", default="python")
    args = ap.parse_args()
    try:
        print(explain_problem(args.slug, args.language))
    except RuntimeError as e:
        sys.exit(f"错误：{e}")


if __name__ == "__main__":
    main()
