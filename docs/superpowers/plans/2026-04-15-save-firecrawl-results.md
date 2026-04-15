# Save Firecrawl Results to knowledge/raw/ Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend `scrape_pipeline.py` to save each Firecrawl search result as a markdown file with YAML frontmatter in `knowledge/raw/`.

**Architecture:** Add a `url_to_slug` helper function to `scrape_pipeline.py`, then after the existing print loop, create the output directory and write one `.md` file per result using today's date and the URL slug as the filename.

**Tech Stack:** Python stdlib (`datetime`, `re`, `pathlib.Path`) — no new dependencies.

---

## File Map

| Action | Path | Purpose |
|--------|------|---------|
| Modify | `scrape_pipeline.py` | Add `url_to_slug`, `datetime` import, and file-saving block |
| Create | `tests/test_scrape_pipeline.py` | Unit tests for `url_to_slug` |
| Create (at runtime) | `knowledge/raw/YYYY-MM-DD_<slug>.md` | One file per Firecrawl result |

---

### Task 1: Extract and test `url_to_slug`

**Files:**
- Modify: `scrape_pipeline.py`
- Create: `tests/test_scrape_pipeline.py`

- [ ] **Step 1: Add `url_to_slug` to `scrape_pipeline.py`**

Add `import datetime` at the top (after existing imports), then add this function before the `load_dotenv()` call:

```python
import datetime

def url_to_slug(url: str) -> str:
    """Convert a URL to a filesystem-safe slug."""
    slug = url.lower()
    slug = re.sub(r'^https?://', '', slug)
    slug = re.sub(r'[^a-z0-9.\-]', '_', slug)
    slug = re.sub(r'_+', '_', slug)   # collapse multiple underscores
    slug = slug.strip('_')
    return slug
```

- [ ] **Step 2: Create `tests/test_scrape_pipeline.py` with failing tests**

```bash
mkdir -p tests
```

```python
# tests/test_scrape_pipeline.py
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from scrape_pipeline import url_to_slug

def test_https_url():
    assert url_to_slug("https://ir.chipotle.com/news-releases") == "ir.chipotle.com_news-releases"

def test_http_url():
    assert url_to_slug("http://ir.chipotle.com/sec-filings") == "ir.chipotle.com_sec-filings"

def test_trailing_slash():
    assert url_to_slug("https://ir.chipotle.com/") == "ir.chipotle.com"

def test_nested_path():
    assert url_to_slug("https://newsroom.chipotle.com/press-releases") == "newsroom.chipotle.com_press-releases"

def test_uppercase_normalized():
    assert url_to_slug("https://Ir.Chipotle.COM/News") == "ir.chipotle.com_news"
```

- [ ] **Step 3: Run tests — expect them to FAIL (function not yet importable)**

```bash
venv/bin/python -m pytest tests/test_scrape_pipeline.py -v
```

Expected: errors like `ImportError` or `cannot import name 'url_to_slug'` — this confirms TDD baseline.

- [ ] **Step 4: Run tests again after adding the function — expect PASS**

```bash
venv/bin/python -m pytest tests/test_scrape_pipeline.py -v
```

Expected output:
```
PASSED tests/test_scrape_pipeline.py::test_https_url
PASSED tests/test_scrape_pipeline.py::test_http_url
PASSED tests/test_scrape_pipeline.py::test_trailing_slash
PASSED tests/test_scrape_pipeline.py::test_nested_path
PASSED tests/test_scrape_pipeline.py::test_uppercase_normalized
5 passed
```

- [ ] **Step 5: Commit**

```bash
git add scrape_pipeline.py tests/test_scrape_pipeline.py
git commit -m "feat: add url_to_slug helper with tests"
```

---

### Task 2: Save results to `knowledge/raw/`

**Files:**
- Modify: `scrape_pipeline.py` (append file-saving block after existing print loop)

- [ ] **Step 1: Add the file-saving block to `scrape_pipeline.py`**

Append this block after the existing `for r in results:` loop:

```python
# --- Step 02: Save results to knowledge/raw/ ---

today = str(datetime.date.today())
output_dir = Path("knowledge/raw")
output_dir.mkdir(parents=True, exist_ok=True)

for r in results:
    slug = url_to_slug(r["url"])
    filename = f"{today}_{slug}.md"
    filepath = output_dir / filename

    frontmatter = f"""---
url: {r['url']}
title: {r['title']}
scraped_at: {today}
---

"""
    content = frontmatter + (r.get("markdown") or "")
    filepath.write_text(content, encoding="utf-8")
    print(f"  Saved: {filepath}")
```

- [ ] **Step 2: Run the script and verify files are created**

```bash
venv/bin/python scrape_pipeline.py
```

Expected output (last lines):
```
  Saved: knowledge/raw/2026-04-15_ir.chipotle.com_news-releases.md
  Saved: knowledge/raw/2026-04-15_newsroom.chipotle.com_press-releases.md
  Saved: knowledge/raw/2026-04-15_ir.chipotle.com.md
  Saved: knowledge/raw/2026-04-15_ir.chipotle.com_financial-releases.md
  Saved: knowledge/raw/2026-04-15_ir.chipotle.com_sec-filings.md
```

- [ ] **Step 3: Spot-check one saved file**

```bash
head -8 knowledge/raw/2026-04-15_ir.chipotle.com_news-releases.md
```

Expected:
```
---
url: https://ir.chipotle.com/news-releases
title: News Releases - Chipotle Mexican Grill
scraped_at: 2026-04-15
---

# News Releases
```

- [ ] **Step 4: Commit**

```bash
git add scrape_pipeline.py knowledge/raw/
git commit -m "feat: save Firecrawl results as markdown files in knowledge/raw/"
```
