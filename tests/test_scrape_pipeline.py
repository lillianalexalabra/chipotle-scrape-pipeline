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
