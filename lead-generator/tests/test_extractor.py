"""Tests for the lead extractor.

No real network calls are made: `requests.Session.get` is monkey-patched to
serve an in-memory fake company website. This also lets the suite run inside
network-restricted CI/sandbox environments.
"""
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.extractor import CrawlConfig, extract_leads  # noqa: E402
from backend.validators import extract_emails, extract_phones, normalize_domain  # noqa: E402

FIXTURES = {
    "https://acme.test": """
        <html><head>
          <title>Home | Acme Robotics</title>
          <meta property="og:site_name" content="Acme Robotics Inc.">
          <script type="application/ld+json">
          {"@type": "Organization", "name": "Acme Robotics Inc.",
           "address": {"@type": "PostalAddress", "streetAddress": "1 Rocket Rd",
                        "addressLocality": "Metropolis", "addressRegion": "CA",
                        "postalCode": "90210"}}
          </script>
        </head><body>
          <nav>
            <a href="/contact">Contact</a>
            <a href="/team">Our Team</a>
            <a href="/products">Products</a>
          </nav>
          <a href="https://www.linkedin.com/company/acme">LinkedIn</a>
          <p>General enquiries: info [at] acme [dot] test</p>
        </body></html>
    """,
    "https://acme.test/contact": """
        <html><body>
          <p>Call us: <a href="tel:+14155550100">+1 415-555-0100</a></p>
          <p>Email: <a href="mailto:sales@acme.test">sales@acme.test</a></p>
        </body></html>
    """,
    "https://acme.test/team": """
        <html><body>
          <div class="card">
            <h3>Jane Doe</h3>
            <p>Head of Sales</p>
            <a href="mailto:jane.doe@acme.test">jane.doe@acme.test</a>
          </div>
          <div class="card">
            <h3>John Smith</h3>
            <p>Founder</p>
            <a href="tel:+14155550101">415-555-0101</a>
          </div>
        </body></html>
    """,
    "https://acme.test/products": "<html><body><p>Our products.</p></body></html>",
}


def _fake_get(self, url, timeout=None, allow_redirects=True):
    url = url.split("#")[0]
    html = FIXTURES.get(url)
    if html is None:
        return SimpleNamespace(status_code=404, text="", headers={}, url=url)
    return SimpleNamespace(status_code=200, text=html, url=url, headers={"Content-Type": "text/html"})


def test_normalize_domain():
    assert normalize_domain("https://Acme.test/about") == "acme.test"
    assert normalize_domain("www.acme.test") == "acme.test"
    assert normalize_domain("acme.test:8080") == "acme.test"


def test_normalize_domain_rejects_garbage():
    with pytest.raises(ValueError):
        normalize_domain("not a domain")
    with pytest.raises(ValueError):
        normalize_domain("")


def test_extract_emails_deobfuscates_and_filters_noise():
    emails = extract_emails("Reach us at info [at] acme [dot] test or noreply@example.com")
    assert "info@acme.test" in emails
    assert "noreply@example.com" not in emails  # blocklisted placeholder domain


def test_extract_phones_formats_international():
    phones = extract_phones("Call +1 415-555-0100 now")
    assert any("415" in p and p.startswith("+1") for p in phones)


@patch("requests.Session.get", new=_fake_get)
def test_full_crawl_extracts_business_and_people():
    result = extract_leads("acme.test", CrawlConfig(max_pages=10, delay_seconds=0))

    assert result.leads, "expected at least one lead"
    assert "https://acme.test/contact" in result.pages_crawled
    assert "https://acme.test/team" in result.pages_crawled
    # The unrelated "/products" page should not have been prioritized/crawled
    # ahead of the budget being used on relevant pages.
    names = {l.contact_name for l in result.leads}
    assert "Jane Doe" in names
    assert "John Smith" in names

    jane = next(l for l in result.leads if l.contact_name == "Jane Doe")
    assert jane.email == "jane.doe@acme.test"
    assert jane.role == "Head of Sales"
    assert jane.business_name == "Acme Robotics Inc."
    assert jane.linkedin == "https://www.linkedin.com/company/acme"
    assert "Metropolis" in jane.address

    john = next(l for l in result.leads if l.contact_name == "John Smith")
    assert "5550101" in john.phone.replace(" ", "").replace("-", "")
    assert john.role == "Founder"

    company_row = next(l for l in result.leads if l.role == "General / Company")
    assert company_row.business_name == "Acme Robotics Inc."
    # jane.doe@acme.test was already claimed by her own lead row, so the
    # fallback company-level row should surface the next distinct address.
    assert company_row.email == "info@acme.test"


@patch("requests.Session.get", new=_fake_get)
def test_respects_robots_disallow():
    class DenyAllRobots(SimpleNamespace):
        def can_fetch(self, *_args):
            return False

    with patch("backend.extractor._get_robot_parser", return_value=DenyAllRobots()):
        result = extract_leads("acme.test", CrawlConfig(max_pages=10, delay_seconds=0, respect_robots=True))
    assert result.pages_crawled == []
    assert any("robots.txt" in w for w in result.warnings)


def test_unreachable_domain_raises_connection_error():
    def _always_fail(self, url, timeout=None, allow_redirects=True):
        raise __import__("requests").exceptions.ConnectionError("boom")

    with patch("requests.Session.get", new=_always_fail):
        with pytest.raises(ConnectionError):
            extract_leads("this-domain-does-not-exist.test", CrawlConfig(delay_seconds=0))
