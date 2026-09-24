# Contributing

Thanks for taking an interest. Bug reports, ideas and pull requests are welcome.

## Development setup

```bash
git clone https://github.com/jingpeng7527/leetcode-toolkit.git
cd leetcode-toolkit
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m pytest tests
```

Python 3.10 or newer is required. The unit tests run offline and need no credentials.

To try the real commands you need your own LeetCode cookies in `.env` (see the README). You can work on the dashboard without any account using `python3 scripts/dashboard.py --demo`.

## Ground rules

- **Never commit secrets or personal data.** That means `.env`, cookies, API keys, `dashboard.html`, and anything in `.cache/`. They are git-ignored; keep it that way. When filing an issue, strip them from logs and screenshots.
- **The ranking model lives in `review/spaced_repetition.py`** as pure functions, and its tests are in `tests/test_spaced_repetition.py`. Changes to how problems are scored should come with a test that would fail without the change.
- **Keep tests offline.** Mock or avoid network calls; CI has no credentials.
- Keep changes focused. One concern per pull request is easier to review.
- If behaviour or configuration changes, update the README in the same pull request.

## Pull requests

1. Fork the repo and create a branch from `main`.
2. Make your change and add or update tests.
3. Run `python -m pytest tests`.
4. Open a pull request and fill in the template. CI runs the tests on Python 3.10 to 3.13.

## Ideas that would be welcome

See the roadmap in the README.
