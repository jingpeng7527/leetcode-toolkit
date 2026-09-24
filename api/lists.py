import json

import config
from api.cache import cached_json
from api.client import AuthError, LeetCodeClient

import requests

NEETCODE_SITE_DATA = "https://raw.githubusercontent.com/neetcode-gh/leetcode/main/.problemSiteData.json"
STUDY_PLANS = {"Top100": "top-100-liked", "Interview150": "top-interview-150"}


def _neetcode_lists() -> dict[str, list[str]]:
    resp = requests.get(NEETCODE_SITE_DATA, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return {
        "NeetCode150": [p["link"].strip("/") for p in data if p.get("neetcode150")],
        "Blind75": [p["link"].strip("/") for p in data if p.get("blind75")],
    }


def load_lists(client: LeetCodeClient, companies: list[str] | None = None) -> dict[str, list[str]]:
    """list name -> problem slugs. Company lists need a Premium session; failures are skipped with a warning."""
    companies = config.COMPANIES if companies is None else companies
    result: dict[str, list[str]] = {}
    result["NeetCode250"] = json.loads((config.DATA_DIR / "neetcode250.json").read_text())
    result.update(cached_json("neetcode_lists", _neetcode_lists))
    for name, plan in STUDY_PLANS.items():
        result[name] = cached_json(f"plan_{plan}", lambda plan=plan: sorted(client.study_plan_slugs(plan)))
    if client.authenticated:
        for company in companies:
            try:
                slugs = cached_json(f"company_{company}", lambda c=company: sorted(client.favorite_slugs(f"{c}-all")))
            except (AuthError, RuntimeError) as e:
                print(f"[warn] 公司题单 {company} 拉取失败：{e}")
                continue
            if slugs:
                result[f"co:{company}"] = slugs
            else:
                print(f"[warn] 公司题单 {company} 为空（账号可能不是 Premium）")
    return result


def hits_by_slug(lists: dict[str, list[str]]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for name, slugs in lists.items():
        for s in slugs:
            out.setdefault(s, []).append(name)
    return out
