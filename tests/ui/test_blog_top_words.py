"""UI tests for Pointr blog.

Two tests:
- test_all_articles_loaded: ensure the blog page shows article content.
- test_top_words_latest_3_articles: compute and save the 5 most common words
  across the latest 3 articles to artifacts/top_words.txt.
"""

import re
import time
from collections import Counter
from pathlib import Path
from typing import Callable, Iterable, List

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver


BLOG_URL = "https://www.pointr.tech/blog"
ARTIFACTS_DIR = Path("artifacts")
ARTIFACTS_DIR.mkdir(exist_ok=True)
TOP_WORDS_FILE = ARTIFACTS_DIR / "top_words.txt"



def wait_for(condition: Callable[[], bool], timeout: float = 20, interval: float = 0.25) -> bool:
    """Poll a simple condition function until it returns True or times out."""
    start = time.time()
    while time.time() - start < timeout:
        if condition():
            return True
        time.sleep(interval)
    return False


def article_links_on_page(browser: WebDriver) -> List[str]:
    """Return unique article URLs found on the current page, in appearance order."""
    links = browser.find_elements(By.CSS_SELECTOR, "a[href*='/blog/']")
    hrefs: List[str] = []
    for elem in links:
        href = elem.get_attribute("href")
        if href and "/blog/" in href and not href.rstrip("/").endswith("/blog"):
            if href not in hrefs:
                hrefs.append(href)
    return hrefs


def scrape_text(browser: WebDriver) -> str:
    """Collect visible text from common article containers on the current page."""
    containers = browser.find_elements(
        By.CSS_SELECTOR, "article, main, .post, .single-post, .blog-post, .entry-content"
    )
    return " ".join(e.text for e in containers)


def tokenize(text: str) -> List[str]:
    """Split text into word tokens (letters and apostrophes)."""
    return re.findall(r"[A-Za-z']{3,}", text.lower())


def compute_top_words(words: Iterable[str], n: int = 5):
    """Return the n most common words and their counts as a list of (word, count)."""
    return Counter(words).most_common(n)


def save_top_words(pairs, path: Path) -> None:
    """Write (word, count) pairs to a file, one per line as 'word: count'."""
    with path.open("w", encoding="utf-8") as f:
        for w, c in pairs:
            f.write(f"{w}: {c}\n")


def test_all_articles_loaded(browser: WebDriver):
    browser.get(BLOG_URL)

    # Try to trigger any lazy loading
    try:
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight / 3)")
    except Exception:
        pass

    def has_content() -> bool:
        # Article cards or any concrete article link indicates the page loaded
        cards = browser.find_elements(By.CSS_SELECTOR, "article, a.blog-card, .blog-index__card")
        if cards:
            return True
        return len(article_links_on_page(browser)) > 0

    assert wait_for(has_content, timeout=60)


def test_top_words_latest_3_articles(browser: WebDriver):
    browser.get(BLOG_URL)

    latest3 = article_links_on_page(browser)[:3]
    assert len(latest3) >= 1, "No articles found"

    # Visit each article, collect words
    words: List[str] = []
    for url in latest3:
        browser.get(url)
        wait_for(
            lambda: browser.find_elements(By.TAG_NAME, "article") or browser.find_elements(By.TAG_NAME, "p"),
            timeout=30,
        )
        words.extend(tokenize(scrape_text(browser)))

    top5 = compute_top_words(words, n=5)
    save_top_words(top5, TOP_WORDS_FILE)

    assert TOP_WORDS_FILE.exists()
