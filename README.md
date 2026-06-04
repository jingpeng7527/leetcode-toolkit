# leetcode-toolkit

> A personal LeetCode integration hub — sync your progress, explore problems, and connect with Claude, Notion, and Obsidian.

## Overview

**leetcode-toolkit** is a Python-based toolchain built on top of the [alfa-leetcode-api](https://github.com/alfaarghya/alfa-leetcode-api). It provides a clean interface to query LeetCode data and pipe it into your personal knowledge workflow.

### What it does

- Fetch your LeetCode profile, solved stats, and submission history
- Browse and filter problems by difficulty, tag, or topic
- Pull the daily challenge automatically
- Sync data to **Notion** (progress tracker, problem notes)
- Export to **Obsidian** (local markdown vault)
- Analyze and explain problems via the **Claude API**

---

## Project Structure

```
leetcode-toolkit/
├── api/
│   ├── client.py          # HTTP client wrapping alfa-leetcode-api
│   └── endpoints.py       # All supported endpoint definitions
├── integrations/
│   ├── claude.py          # Claude API — problem explanations & hints
│   ├── notion.py          # Notion API — sync submissions & notes
│   └── obsidian.py        # Obsidian — write markdown to local vault
├── scripts/
│   ├── daily.py           # Fetch and log today's daily problem
│   └── sync.py            # Full sync: LeetCode → Notion + Obsidian
├── config.py              # API keys and settings (loaded from .env)
├── requirements.txt
└── README.md
```

---

## Supported Endpoints

All data is fetched via [alfa-leetcode-api](https://github.com/alfaarghya/alfa-leetcode-api).

| Category | Endpoint | Description |
|----------|----------|-------------|
| User | `/:username` | Profile overview |
| User | `/:username/solved` | Total solved by difficulty |
| User | `/:username/submission` | Last N submissions |
| User | `/:username/acSubmission` | Last N accepted submissions |
| User | `/:username/calendar` | Submission heatmap |
| User | `/:username/skill` | Skill stats by tag |
| Problems | `/daily` | Today's daily challenge |
| Problems | `/select?titleSlug=...` | Problem detail by slug |
| Problems | `/problems?difficulty=MEDIUM&tags=dp` | Filtered problem list |
| Contests | `/contests/upcoming` | Upcoming contest schedule |

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/leetcode-toolkit.git
cd leetcode-toolkit
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` with your keys:

```env
LEETCODE_USERNAME=your_username

# Optional integrations
ANTHROPIC_API_KEY=sk-...
NOTION_API_KEY=secret_...
NOTION_DATABASE_ID=...
OBSIDIAN_VAULT_PATH=/path/to/your/vault
```

---

## Usage

### Fetch your profile

```python
from api.client import LeetCodeClient

client = LeetCodeClient()
profile = client.get_profile("your_username")
print(profile)
```

### Get today's daily problem

```bash
python scripts/daily.py
```

### Sync recent submissions to Notion

```bash
python scripts/sync.py --target notion --limit 10
```

### Export problem notes to Obsidian

```bash
python scripts/sync.py --target obsidian
```

---

## Integrations

### Claude

Uses the Anthropic API to generate problem explanations, complexity analysis, and hints on demand.

```python
from integrations.claude import explain_problem

explain_problem(title_slug="two-sum", language="python")
```

### Notion

Syncs accepted submissions and problem metadata to a Notion database. Each entry includes title, difficulty, tags, submission date, and a link to the problem.

### Obsidian

Writes structured markdown notes to your local Obsidian vault, organized by topic or difficulty.

---

## Roadmap

- [x] Core API client
- [x] User stats and submission history
- [x] Daily problem fetch
- [ ] Notion sync
- [ ] Obsidian export
- [ ] Claude problem explainer
- [ ] CLI interface
- [ ] GitHub Actions for daily auto-sync

---

## Credits

- LeetCode data powered by [alfa-leetcode-api](https://github.com/alfaarghya/alfa-leetcode-api)
- AI features powered by [Anthropic Claude](https://www.anthropic.com)

---

## License

MIT
