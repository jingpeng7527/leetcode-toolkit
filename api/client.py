import requests

import config
from api import queries

GRAPHQL_URL = "https://leetcode.com/graphql"


class AuthError(RuntimeError):
    pass


class LeetCodeClient:
    def __init__(self, session: str | None = None, csrftoken: str | None = None):
        session = session if session is not None else config.LEETCODE_SESSION
        csrftoken = csrftoken if csrftoken is not None else config.LEETCODE_CSRFTOKEN
        self.authenticated = bool(session and csrftoken)
        self.http = requests.Session()
        self.http.headers.update({"Content-Type": "application/json", "Referer": "https://leetcode.com"})
        if self.authenticated:
            self.http.headers["x-csrftoken"] = csrftoken
            self.http.cookies.set("LEETCODE_SESSION", session, domain="leetcode.com")
            self.http.cookies.set("csrftoken", csrftoken, domain="leetcode.com")

    def query(self, query: str, variables: dict | None = None) -> dict:
        resp = self.http.post(GRAPHQL_URL, json={"query": query, "variables": variables or {}}, timeout=30)
        if resp.status_code in (401, 403):
            raise AuthError("LeetCode 拒绝了请求：Cookie 可能已失效，请重新从浏览器复制 LEETCODE_SESSION / csrftoken")
        resp.raise_for_status()
        body = resp.json()
        if body.get("errors"):
            raise RuntimeError(f"GraphQL error: {body['errors'][0].get('message')}")
        return body["data"]

    def all_submissions(self) -> list[dict]:
        """Full submission history (needs login). Paginates via offset/lastKey until hasNext is false."""
        if not self.authenticated:
            raise AuthError("拉取完整提交历史需要 LEETCODE_SESSION 和 LEETCODE_CSRFTOKEN（见 .env.example）")
        out, offset, last_key, limit = [], 0, None, 20
        while True:
            page = self.query(queries.SUBMISSION_LIST, {"offset": offset, "limit": limit, "lastKey": last_key})["submissionList"]
            out.extend(page["submissions"] or [])
            if not page["hasNext"]:
                return out
            offset += limit
            last_key = page.get("lastKey")

    def problemset(self) -> list[dict]:
        """All problems: titleSlug, difficulty, questionFrontendId."""
        out, skip = [], 0
        while True:
            page = self.query(queries.PROBLEMSET, {"skip": skip, "limit": 100})["problemsetQuestionList"]
            out.extend(page["questions"])
            skip += 100
            if skip >= page["total"]:
                return out

    def tags_by_slug(self) -> dict[str, list[str]]:
        return {q["titleSlug"]: [t["name"] for t in q["topicTags"]] for q in self.problemset()}

    def difficulties(self) -> dict[str, str]:
        return {q["titleSlug"]: q["difficulty"] for q in self.problemset()}

    def slugs_by_number(self) -> dict[int, str]:
        return {int(q["questionFrontendId"]): q["titleSlug"] for q in self.problemset() if str(q["questionFrontendId"]).isdigit()}

    def study_plan_slugs(self, plan_slug: str) -> set[str]:
        groups = self.query(queries.STUDY_PLAN, {"slug": plan_slug})["studyPlanV2Detail"]["planSubGroups"]
        return {q["titleSlug"] for g in groups for q in g["questions"]}

    def favorite_slugs(self, favorite_slug: str) -> set[str]:
        out, skip = set(), 0
        while True:
            page = self.query(queries.FAVORITE_LIST, {"favoriteSlug": favorite_slug, "skip": skip, "limit": 100})["favoriteQuestionList"]
            out |= {q["titleSlug"] for q in page["questions"]}
            if not page["hasMore"]:
                return out
            skip += 100

    def daily_challenge(self) -> dict:
        return self.query(queries.DAILY)["activeDailyCodingChallengeQuestion"]

    def question_detail(self, title_slug: str) -> dict:
        return self.query(queries.QUESTION_DETAIL, {"titleSlug": title_slug})["question"]
