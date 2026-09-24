# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- Spaced-repetition ranking over the full submission history, weighted by
  zerotrac contest rating and by membership in NeetCode 250 / 150, Blind 75,
  LeetCode Top 100, Top Interview 150 and company lists.
- `scripts/review.py` to print or export today's review queue.
- Notion sync (`scripts/sync.py`) with linking of existing notes by problem number.
- Local HTML dashboard (`scripts/dashboard.py`) and a synthetic-data demo mode (`--demo`).
- Claude problem hints (`scripts/explain.py`) and daily challenge (`scripts/daily.py`).
- Unit tests and a GitHub Actions workflow.
