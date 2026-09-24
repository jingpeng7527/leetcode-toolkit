# leetcode-toolkit

> Find the LeetCode problems worth redoing today, using a spaced-repetition (memory curve) model over your full submission history — then sync them to Notion and browse them in a local dashboard.

## What it does

- Pulls your **full** submission history from LeetCode's GraphQL API using your own session cookie. (The public `alfa-leetcode-api` only exposes the latest ~20 submissions and cannot paginate, so it cannot support this.)
- Scores every solved problem with a forgetting-curve model and ranks what to redo first.
- Weights problems that show up in well-known lists: NeetCode 250 / 150, Blind 75, LeetCode Top 100, Top Interview 150, and company lists (Google, Apple, … — needs LeetCode Premium).
- Syncs the ranked list to a Notion database and links your existing Notion notes to it.
- Generates a local HTML dashboard (queue, retention distribution, forgetting curve, heatmap, list coverage).
- Optional: explain a problem with Claude (hints first, not full code), and print today's daily challenge.

## How the ranking works

1. Only accepted submissions count. `times_solved` is how many times you got a problem accepted.
2. Base interval grows with each successful repeat: `1, 3, 7, 16, 35, 75, 160` days (then ×1.5 each time).
3. The interval is scaled by difficulty:
   - With a [zerotrac](https://zerotrac.github.io/leetcode_problem_rating/) contest rating: `clamp(1.3 - (rating - 1200) / 2000, 0.6, 1.3)`, and problems rated **above 2000 are postponed** (×1.5).
   - Without a rating: Easy 1.3 / Medium 1.0 / Hard 0.7.
4. Every list or company a problem appears in shortens its interval: `interval / (1 + 0.1 × hits)`.
5. Retention halves every interval: `0.5 ^ (days since last AC / interval)`. A problem is **due** once retention ≤ 50%.
6. Ranking = `forget_probability × (1 + 0.25 × hits)`, so among long-forgotten problems the ones that appear in more lists come first.

All constants are at the top of [review/spaced_repetition.py](review/spaced_repetition.py).

## Setup

```bash
git clone https://github.com/jingpeng7527/leetcode-toolkit.git
cd leetcode-toolkit
pip3 install -r requirements.txt
cp .env.example .env
```

Edit `.env`:

| Variable | Needed for |
|---|---|
| `LEETCODE_SESSION`, `LEETCODE_CSRFTOKEN` | Everything that reads your history. Copy from your browser: DevTools → Application → Cookies → `leetcode.com`. Treat them like a password. |
| `COMPANIES` | Company lists, comma separated (default `google,apple`). Needs Premium; lists that cannot be fetched are skipped with a warning. |
| `NOTION_API_KEY`, `NOTION_DATABASE_ID` | Notion sync |
| `NOTION_NOTES_PAGE_ID` | Linking existing Notion notes (optional) |
| `ANTHROPIC_API_KEY` | `explain.py` (optional) |

`.env`, `.cache/` and `dashboard.html` are git-ignored.

## Usage

```bash
python3 scripts/review.py                  # today's review queue (add --all, --limit N, --export out.csv)
python3 scripts/dashboard.py               # build and open dashboard.html
python3 scripts/sync.py                    # sync the top 50 to Notion (--limit N, --all)
python3 scripts/daily.py                   # today's daily challenge
python3 scripts/explain.py two-sum         # Claude hints for a problem (--language python)
python3 -m pytest tests                    # unit tests
```

## Notion setup

**Review database** — create a database with these exact property names and types:

`Name` (title), `Slug` (text), `Difficulty` (select), `Rating` (number), `Last AC` (date), `AC Count` (number), `Overdue Days` (number), `Lists` (multi-select), `URL` (url). Share it with your Notion integration. Rows are upserted by `Slug`, so re-running updates instead of duplicating.

**Linking your notes** (optional) — add `Notes` (url) and `Topic` (select) columns, set `NOTION_NOTES_PAGE_ID` to your notes root page, and share that page with the integration (••• → Connections). The sync scans the child pages (and pages one level below, including inside toggles), reads the problem number from a page title such as `76. Minimum Window Substring` or `滑动窗口 - 3. Longest Substring…`, and fills `Notes` with the page link and `Topic` with the parent page's name. Problems you have notes for are synced even if they fall outside the top N.

## Project structure

```
api/
  client.py          authenticated GraphQL client (history, problemset, study plans, company lists, daily)
  queries.py         GraphQL query strings
  rating.py          zerotrac ratings (slug -> rating), cached
  lists.py           list membership (slug -> lists), cached
  cache.py           tiny JSON file cache in .cache/
review/
  models.py          Submission, ProblemReview
  spaced_repetition.py   the scoring model (pure functions, unit-tested)
  pipeline.py        fetch everything and return ranked reviews
integrations/
  notion.py          upsert reviews into a Notion database
  notion_notes.py    crawl your notes and map them to problems
  claude.py          problem explanations via the Anthropic API
scripts/             review, dashboard, sync, daily, explain
data/neetcode250.json   NeetCode 250 slugs (extracted from neetcode.io, which flags them in its site data)
tests/
```

## Caveats

- `submissionList` pagination (offset + `lastKey`) is written from public documentation of LeetCode's GraphQL API; LeetCode can change it without notice. Only leetcode.com is supported, not leetcode.cn.
- Ratings exist only for problems that appeared in contests (~2,600); everything else falls back to Easy/Medium/Hard.
- The NeetCode 250 list is a snapshot in `data/neetcode250.json`; re-extract it if NeetCode changes the list.
- Your cookie expires; if requests start failing with an auth error, copy fresh values into `.env`.

## Credits

- Contest ratings: [zerotrac/leetcode_problem_rating](https://github.com/zerotrac/leetcode_problem_rating)
- NeetCode 150 / Blind 75 flags: [neetcode-gh/leetcode](https://github.com/neetcode-gh/leetcode)

## License

MIT
