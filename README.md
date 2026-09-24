# leetcode-toolkit

You solve hundreds of problems and forget them a few months later. This tool reads your full LeetCode submission history and uses a spaced-repetition (memory curve) model to pick **the problems most worth redoing today**, favoring ones that keep showing up in NeetCode 250, Top 100, Top Interview 150 and company lists like Google and Apple. It can sync the list to Notion and build a local dashboard.

**[Live demo](https://leetcode-review.netlify.app/)** — the dashboard rendered from randomly generated sample data (not a real submission history). Regenerate it with `python3 scripts/dashboard.py --demo`.

## Quick start

```bash
git clone https://github.com/jingpeng7527/leetcode-toolkit.git
cd leetcode-toolkit
pip3 install -r requirements.txt
cp .env.example .env      # then fill in your LeetCode cookies, see below
python3 scripts/review.py
```

**Getting your cookies**: log in to leetcode.com → DevTools → Application → Cookies, and copy `LEETCODE_SESSION` and `csrftoken` into `.env`. They are equivalent to your login, so never share them or commit them (`.env` is git-ignored).

## Commands

| Command | What it does |
|---|---|
| `python3 scripts/review.py` | Print today's review queue in the terminal (`--all` for everything, `--export out.csv` to save) |
| `python3 scripts/dashboard.py` | Build and open a local dashboard: review queue, forgetting curve, activity heatmap, list coverage |
| `python3 scripts/sync.py` | Sync the top 50 problems to Notion (`--limit N` to change) |
| `python3 scripts/explain.py two-sum` | Layered hints from Claude for a problem, without giving away the full solution |
| `python3 scripts/daily.py` | Today's daily challenge |

## How the ranking works

- Each successful redo stretches the next interval: 1, 3, 7, 16, 35, 75, 160 days.
- Harder problems get shorter intervals; problems rated above 2000 (zerotrac contest rating) are pushed back.
- The more lists a problem appears in (NeetCode, Top 100, company lists, …), the shorter its interval and the higher it ranks.
- A problem is due once more than one interval has passed since your last accepted submission.

All the numbers live at the top of [review/spaced_repetition.py](review/spaced_repetition.py) if you want to tune them.

## Optional configuration

Set these in `.env` as needed:

- **Company lists** (`COMPANIES=google,apple`): needs cookies from a LeetCode Premium account. Lists that can't be fetched are skipped.
- **Notion sync**: set `NOTION_API_KEY` and `NOTION_DATABASE_ID`. The database needs these properties: `Name` (title), `Slug` (text), `Difficulty` (select), `Rating`, `AC Count`, `Overdue Days` (number), `Last AC` (date), `Lists` (multi-select), `URL` (url). Share the database with your integration.
- **Linking your existing notes**: add `Notes` (url) and `Topic` (select) properties, and set `NOTION_NOTES_PAGE_ID` to your notes root page (also shared with the integration). A note page is matched by the problem number in its title, e.g. `76. Minimum Window Substring`.
- **Claude explanations**: set `ANTHROPIC_API_KEY`.

## Caveats

- leetcode.com only; leetcode.cn is not supported.
- Full submission history comes from an undocumented LeetCode GraphQL endpoint, which may change.
- Contest ratings cover only about 2,600 problems that appeared in contests; the rest fall back to Easy / Medium / Hard.
- Cookies expire. If you get an auth error, copy fresh ones into `.env`.

## Credits

Ratings from [zerotrac/leetcode_problem_rating](https://github.com/zerotrac/leetcode_problem_rating); NeetCode lists from [neetcode-gh/leetcode](https://github.com/neetcode-gh/leetcode).

MIT License
