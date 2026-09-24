import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).parent
load_dotenv(ROOT / ".env")

CACHE_DIR = ROOT / ".cache"
DATA_DIR = ROOT / "data"

LEETCODE_SESSION = os.getenv("LEETCODE_SESSION", "")
LEETCODE_CSRFTOKEN = os.getenv("LEETCODE_CSRFTOKEN", "")
EXCLUDE_DIFFICULTIES = {d.strip().capitalize() for d in os.getenv("EXCLUDE_DIFFICULTIES", "Easy").split(",") if d.strip()}
COMPANIES = [c.strip() for c in os.getenv("COMPANIES", "google,apple").split(",") if c.strip()]

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
NOTION_API_KEY = os.getenv("NOTION_API_KEY", "")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID", "")
NOTION_NOTES_PAGE_ID = os.getenv("NOTION_NOTES_PAGE_ID", "")
