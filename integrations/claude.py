import re

import anthropic

import config
from api.client import LeetCodeClient

MODEL = "claude-sonnet-5"

SYSTEM = (
    "你是算法面试教练。用户正在复习一道做过的 LeetCode 题。"
    "先给分层提示（不要直接给完整代码），再给核心思路、时间/空间复杂度，最后列出常见坑。用中文回答。"
)


def _strip_html(html: str) -> str:
    return re.sub(r"\n{3,}", "\n\n", re.sub(r"<[^>]+>", "", html or "")).replace("&nbsp;", " ").replace("&lt;", "<").replace("&gt;", ">")


def explain_problem(title_slug: str, language: str = "python", client: LeetCodeClient | None = None) -> str:
    if not config.ANTHROPIC_API_KEY:
        raise RuntimeError("需要在 .env 里设置 ANTHROPIC_API_KEY")
    q = (client or LeetCodeClient()).question_detail(title_slug)
    prompt = (
        f"题目：{q['title']}（{q['difficulty']}），标签：{', '.join(t['name'] for t in q['topicTags'])}\n"
        f"我用 {language}。\n\n{_strip_html(q['content'])}"
    )
    msg = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY).messages.create(
        model=MODEL, max_tokens=2000, system=SYSTEM, messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text
