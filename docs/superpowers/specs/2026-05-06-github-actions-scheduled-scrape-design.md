# Design: GitHub Actions Scheduled Scrape

**Date:** 2026-05-06
**Status:** Approved

## Goal

Run `scrape_pipeline.py` on a daily schedule via GitHub Actions, then automatically commit any new `knowledge/raw/` files back to `main`.

## Files Changed

| File | Change |
|------|--------|
| `scrape_pipeline.py` | Wrap module-level code in `if __name__ == "__main__":` guard |
| `.github/workflows/scrape.yml` | New — scheduled workflow |

## Workflow Structure

**Triggers:**
- `schedule`: daily at 08:00 UTC (`cron: '0 8 * * *'`)
- `workflow_dispatch`: manual trigger from the GitHub Actions UI

**Steps:**
1. `actions/checkout@v4` — check out the repo
2. `actions/setup-python@v5` — Python 3.12
3. `pip install -r requirements.txt`
4. `python scrape_pipeline.py` — with `FIRECRAWL_API_KEY` injected from the repo secret of the same name
5. Commit and push `knowledge/raw/`:
   ```sh
   git config user.name "github-actions[bot]"
   git config user.email "github-actions[bot]@users.noreply.github.com"
   git add knowledge/raw/
   git diff --cached --quiet || (git commit -m "chore: scrape $(date +%Y-%m-%d)" && git push)
   ```
   The `git diff --cached --quiet ||` guard skips the commit entirely when no new files were produced.

## Secret Setup (manual, one-time)

Add the Firecrawl API key as a repository secret before the workflow can run:

- **Path:** Repo → Settings → Secrets and variables → Actions → New repository secret
- **Name:** `FIRECRAWL_API_KEY`
- **Value:** the key from your local `.env` file

`GITHUB_TOKEN` is provided automatically by GitHub Actions and has sufficient write permission to commit and push to `main`.

## Out of Scope

- Deduplication / skip-if-exists logic for files already in `knowledge/raw/`
- Notifications or alerts on scrape failure
- Any downstream processing of saved markdown files
