"""Input validation and text-extraction helpers (domains, emails, phones)."""
from __future__ import annotations

import re
from urllib.parse import urlparse

import phonenumbers

DOMAIN_RE = re.compile(
    r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.(?!-)[A-Za-z0-9-]{1,63}(?<!-))+$"
)

EMAIL_RE = re.compile(
    r"[a-zA-Z0-9][a-zA-Z0-9._%+\-]*@[a-zA-Z0-9][a-zA-Z0-9.\-]*\.[a-zA-Z]{2,}"
)

IMAGE_EXT_RE = re.compile(r"\.(png|jpe?g|gif|svg|webp|bmp|ico)$", re.IGNORECASE)

# Domains that only ever show up via analytics/CMS boilerplate, never a real
# business contact -- filtering these out avoids a lot of false positives.
EMAIL_DOMAIN_BLOCKLIST = {
    "example.com", "sentry.io", "sentry-next.wixpress.com", "wixpress.com",
    "godaddy.com", "schema.org", "w3.org", "gstatic.com", "google.com",
    "cloudflare.com", "youremail.com", "domain.com", "yourdomain.com",
}

DEOBFUSCATE_STEPS = [
    (re.compile(r"\s*\[\s*at\s*\]\s*|\s*\(\s*at\s*\)\s*", re.IGNORECASE), "@"),
    (re.compile(r"\s+at\s+", re.IGNORECASE), "@"),
    (re.compile(r"\s*\[\s*dot\s*\]\s*|\s*\(\s*dot\s*\)\s*", re.IGNORECASE), "."),
    (re.compile(r"\s+dot\s+", re.IGNORECASE), "."),
]


def normalize_domain(raw: str) -> str:
    """Turn free-form user input ("https://Acme.com/about", "acme.com/") into
    a bare, lowercase domain ("acme.com"). Raises ValueError if it doesn't
    look like a real domain.
    """
    raw = (raw or "").strip()
    if not raw:
        raise ValueError("Please enter a domain.")
    candidate = raw if "://" in raw else "//" + raw
    parsed = urlparse(candidate, scheme="https")
    host = (parsed.netloc or parsed.path).split("/")[0].strip().lower()
    host = host.split("@")[-1]  # drop any accidental user@ prefix
    host = host.split(":")[0]  # drop a port suffix
    if host.startswith("www."):
        host = host[4:]
    if not DOMAIN_RE.match(host):
        raise ValueError(f"'{raw}' doesn't look like a valid domain, e.g. acme.com")
    return host


def deobfuscate(text: str) -> str:
    for pattern, repl in DEOBFUSCATE_STEPS:
        text = pattern.sub(repl, text)
    return text


def extract_emails(text: str) -> set[str]:
    found: set[str] = set()
    if not text:
        return found
    for candidate in EMAIL_RE.findall(deobfuscate(text)):
        candidate = candidate.strip(".,;:")
        if IMAGE_EXT_RE.search(candidate):
            continue
        domain = candidate.rsplit("@", 1)[-1].lower()
        if domain in EMAIL_DOMAIN_BLOCKLIST:
            continue
        found.add(candidate.lower())
    return found


def extract_phones(text: str, default_region: str = "US") -> set[str]:
    found: set[str] = set()
    if not text:
        return found
    try:
        for match in phonenumbers.PhoneNumberMatcher(text, default_region):
            found.add(
                phonenumbers.format_number(
                    match.number, phonenumbers.PhoneNumberFormat.INTERNATIONAL
                )
            )
    except Exception:
        pass
    return found
