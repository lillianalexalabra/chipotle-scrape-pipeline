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

data = response.json() # convert response to JSON
results = data["data"]["web"] #get the results from the response
print(f"Firecrawl returned {len(results)} results")

for r in results:
    print(f"  - {r['title']}")
    print(f"    {r['url']}")
    print(f"    markdown length: {len(r.get('markdown') or '')} chars")