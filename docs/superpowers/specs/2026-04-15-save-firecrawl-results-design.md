# Design: Save Firecrawl Results to knowledge/raw/

**Date:** 2026-04-15  
**Status:** Approved

## Goal

Extend `scrape_pipeline.py` so that each Firecrawl search result is saved as a markdown file in `knowledge/raw/`, with metadata frontmatter and a filename derived from the run date and source URL.

## Filename Convention

```
knowledge/raw/YYYY-MM-DD_<url-slug>.md
```

- Date: the date the script ran (from `datetime.date.today()`)
- URL slug: strip `https://`, replace `/` and non-alphanumeric characters with `_`, lowercase

**Examples:**

| URL | Filename |
|-----|----------|
| `https://ir.chipotle.com/news-releases` | `2026-04-15_ir.chipotle.com_news-releases.md` |
| `https://newsroom.chipotle.com/press-releases` | `2026-04-15_newsroom.chipotle.com_press-releases.md` |
| `https://ir.chipotle.com/sec-filings` | `2026-04-15_ir.chipotle.com_sec-filings.md` |

## File Contents

Each file starts with a YAML frontmatter block, then the raw markdown scraped by Firecrawl:

```markdown
---
url: https://ir.chipotle.com/news-releases
title: News Releases - Chipotle Mexican Grill
scraped_at: 2026-04-15
---

(raw markdown content from Firecrawl)
```

## Code Changes

All changes are confined to `scrape_pipeline.py`. No new files or dependencies are introduced.

1. Import `datetime` (stdlib, already available)
2. Create `knowledge/raw/` with `Path.mkdir(parents=True, exist_ok=True)` — no-op if it already exists
3. After the existing print loop, iterate over results and for each:
   - Build the URL slug with `re.sub(r'[^a-z0-9.\-]', '_', url.lower().replace('https://', '').replace('http://', ''))`
   - Build the filename: `f"{today}_{slug}.md"`
   - Write frontmatter + markdown to `knowledge/raw/<filename>`
   - Print a confirmation line: `Saved: knowledge/raw/<filename>`

## Out of Scope

- Skip-if-exists logic (can be added later if the script is run multiple times per day)
- Cleaning or post-processing the markdown content
- Any downstream indexing or summarization of saved files
