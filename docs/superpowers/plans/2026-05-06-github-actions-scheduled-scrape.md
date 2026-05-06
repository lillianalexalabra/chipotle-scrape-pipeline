# GitHub Actions Scheduled Scrape Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Run `scrape_pipeline.py` daily via GitHub Actions and auto-commit any new `knowledge/raw/` files back to `main`.

**Architecture:** Add an `if __name__ == "__main__":` guard to `scrape_pipeline.py` so the API call only fires when the script is run directly, then add a workflow file that installs deps, runs the script, and commits new files using plain git with a no-op guard for days with no changes.

**Tech Stack:** GitHub Actions, Python 3.12, `requests`, `python-dotenv`, GitHub-hosted runners (`ubuntu-latest`)

---

## File Map

| File | Change |
|------|--------|
| `scrape_pipeline.py` | Wrap lines 20–69 in `if __name__ == "__main__":` |
| `tests/test_scrape_pipeline.py` | Add test verifying import does not trigger network call |
| `.github/workflows/scrape.yml` | New — scheduled workflow |

---

### Task 1: Guard `scrape_pipeline.py` against import-time side effects

**Files:**
- Modify: `scrape_pipeline.py`
- Test: `tests/test_scrape_pipeline.py`

- [ ] **Step 1: Write the failing test**

Add this test to `tests/test_scrape_pipeline.py`:

```python
def test_import_does_not_make_network_calls(monkeypatch):
    import importlib
    import scrape_pipeline as sp

    called = []
    monkeypatch.setattr("requests.post", lambda *a, **kw: called.append(True))
    importlib.reload(sp)
    assert called == [], "importing scrape_pipeline should not make a network call"
```

- [ ] **Step 2: Run the test to confirm it fails**

```bash
cd /Users/alexalabra/isba-4715/chipotle-scrape-pipeline
source venv/bin/activate
pytest tests/test_scrape_pipeline.py::test_import_does_not_make_network_calls -v
```

Expected output: `FAILED` — the reload currently triggers `requests.post`.

- [ ] **Step 3: Add the `if __name__ == "__main__":` guard**

In `scrape_pipeline.py`, the file should look like this after the change (the `url_to_slug` function and imports stay at the top level; everything after `load_dotenv()` moves inside the guard):

```python
import datetime
import os
import re
import time
from pathlib import Path
from dotenv import load_dotenv
import requests


def url_to_slug(url: str) -> str:
    """Convert a URL to a filesystem-safe slug."""
    slug = url.lower()
    slug = re.sub(r'^https?://', '', slug)
    slug = re.sub(r'[^a-z0-9.\-]', '_', slug)
    slug = re.sub(r'_+', '_', slug)
    slug = slug.strip('_')
    return slug


if __name__ == "__main__":
    load_dotenv()

    api_key = os.getenv("FIRECRAWL_API_KEY")

    # --- Step 01: Search + scrape with Firecrawl ---

    api_url = "https://api.firecrawl.dev/v2/search"

    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "query": "Chipotle investor relations press releases",
        "limit": 5,
        "scrapeOptions": {"formats": ["markdown"]}
    }

    response = requests.post(api_url, headers=headers, json=payload)

    data = response.json()
    results = data["data"]["web"]
    print(f"Firecrawl returned {len(results)} results")

    for r in results:
        print(f"  - {r['title']}")
        print(f"    {r['url']}")
        print(f"    markdown length: {len(r.get('markdown') or '')} chars")

    # --- Step 02: Save results to knowledge/raw/ ---

    today = str(datetime.date.today())
    output_dir = Path("knowledge/raw")
    output_dir.mkdir(parents=True, exist_ok=True)

    for r in results:
        slug = url_to_slug(r["url"])
        filename = f"{today}_{slug}.md"
        filepath = output_dir / filename

        frontmatter = f"""---
url: "{r['url']}"
title: "{r['title']}"
scraped_at: {today}
---

"""
        content = frontmatter + (r.get("markdown") or "")
        filepath.write_text(content, encoding="utf-8")
        print(f"Saved: knowledge/raw/{filename}")
```

- [ ] **Step 4: Run all tests to confirm they pass**

```bash
pytest tests/test_scrape_pipeline.py -v
```

Expected output: all 6 tests `PASSED`.

- [ ] **Step 5: Commit**

```bash
git add scrape_pipeline.py tests/test_scrape_pipeline.py
git commit -m "refactor: guard scrape_pipeline against import-time side effects"
```

---

### Task 2: Create the GitHub Actions workflow

**Files:**
- Create: `.github/workflows/scrape.yml`

- [ ] **Step 1: Create the `.github/workflows/` directory and workflow file**

```bash
mkdir -p .github/workflows
```

Create `.github/workflows/scrape.yml` with this exact content:

```yaml
name: Daily Chipotle Scrape

on:
  schedule:
    - cron: '0 8 * * *'
  workflow_dispatch:

jobs:
  scrape:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repo
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run scrape pipeline
        env:
          FIRECRAWL_API_KEY: ${{ secrets.FIRECRAWL_API_KEY }}
        run: python scrape_pipeline.py

      - name: Commit new sources
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add knowledge/raw/
          git diff --cached --quiet || (git commit -m "chore: scrape $(date +%Y-%m-%d)" && git push)
```

- [ ] **Step 2: Validate the YAML is well-formed**

```bash
python -c "import yaml; yaml.safe_load(open('.github/workflows/scrape.yml')); print('YAML valid')"
```

Expected output: `YAML valid`

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/scrape.yml
git commit -m "feat: add GitHub Actions daily scrape workflow"
```

---

## One-Time Manual Step (after pushing)

Before the workflow can run, add the Firecrawl API key as a GitHub repository secret:

1. Go to your repo on GitHub → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Name: `FIRECRAWL_API_KEY`
4. Value: the key from your local `.env` file
5. Click **Add secret**

You can verify the workflow triggers correctly by going to **Actions** → **Daily Chipotle Scrape** → **Run workflow**.
