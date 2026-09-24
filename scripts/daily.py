import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from api.client import LeetCodeClient


def main():
    d = LeetCodeClient().daily_challenge()
    q = d["question"]
    tags = ", ".join(t["name"] for t in q["topicTags"])
    print(f"{d['date']}  {q['title']} [{q['difficulty']}]")
    print(f"https://leetcode.com{d['link']}")
    print(f"tags: {tags}")


if __name__ == "__main__":
    main()
