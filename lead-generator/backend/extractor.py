"""Crawls a single business domain and compiles its publicly listed contact
details into a table of "leads" (one row per person found, plus a fallback
row for the company itself).

Design notes / scope:
  - This only ever visits pages that live on the domain the user entered
    (the site's own homepage, plus same-domain pages it links to that look
    like contact/about/team pages). It never logs into anything and never
    queries third-party directories.
  - It is intentionally polite: it honours robots.txt by default, sends a
    descriptive User-Agent, rate-limits itself, and bounds the number of
    pages it will fetch per run.
"""
from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field
from urllib import robotparser
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from .models import Lead
from .validators import extract_emails, extract_phones, normalize_domain

USER_AGENT = (
    "Mozilla/5.0 (compatible; LeadGeneratorBot/1.0; "
    "+https://github.com/bajpaishivanshu67-sudo/VoteCast)"
)

# Used only as a fallback when a homepage doesn't link to anything that looks
# like a contact/about/team page (e.g. JS-driven nav with no readable hrefs).
FALLBACK_PATHS = ["contact", "contact-us", "about", "about-us", "team"]

NAV_KEYWORDS = (
    "contact", "about", "team", "staff", "leadership", "people",
    "location", "office", "management", "meet", "founder", "our-story",
)

SOCIAL_DOMAINS = {
    "linkedin.com": "linkedin",
    "twitter.com": "twitter",
    "x.com": "twitter",
    "facebook.com": "facebook",
    "instagram.com": "instagram",
}

ROLE_KEYWORDS = (
    "chief executive", "ceo", "cto", "cfo", "coo", "founder", "co-founder",
    "president", "vice president", "vp ", "director", "manager",
    "head of", "officer", "sales", "marketing", "partner", "principal",
    "owner", "lead ",
)

# Two-to-four Title-Case words, e.g. "Jane Doe" or "Mary Anne O'Neil".
NAME_RE = re.compile(r"^[A-Z][A-Za-z.'-]+(?:\s+[A-Z][A-Za-z.'-]+){1,3}$")


@dataclass
class CrawlConfig:
    max_pages: int = 15
    delay_seconds: float = 0.5
    timeout_seconds: int = 8
    respect_robots: bool = True
    default_region: str = "US"


@dataclass
class CrawlResult:
    leads: list[Lead] = field(default_factory=list)
    pages_crawled: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def _get_robot_parser(session: requests.Session, base_url: str, timeout: int):
    rp = robotparser.RobotFileParser()
    try:
        resp = session.get(urljoin(base_url, "/robots.txt"), timeout=timeout)
        if resp.status_code == 200:
            rp.parse(resp.text.splitlines())
        else:
            rp.allow_all = True
    except requests.RequestException:
        rp.allow_all = True
    return rp


def _resolve_base_url(session: requests.Session, domain: str, timeout: int):
    last_error = None
    for scheme in ("https", "http"):
        url = f"{scheme}://{domain}"
        try:
            resp = session.get(url, timeout=timeout, allow_redirects=True)
            if resp.status_code < 400:
                return resp.url, resp
            last_error = f"HTTP {resp.status_code}"
        except requests.RequestException as exc:
            last_error = exc
    raise ConnectionError(
        f"Could not reach '{domain}' over HTTPS or HTTP ({last_error}). "
        "Double-check the domain is correct and publicly reachable."
    )


def _same_domain(url: str, root_netloc: str) -> bool:
    netloc = urlparse(url).netloc.lower()
    return netloc == root_netloc or netloc.endswith("." + root_netloc)


def _extract_jsonld(soup: BeautifulSoup):
    """Yield parsed JSON-LD objects, flattening @graph / top-level lists."""
    for tag in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(tag.string or "")
        except (ValueError, TypeError):
            continue
        items = data if isinstance(data, list) else [data]
        flattened = []
        for item in items:
            if isinstance(item, dict) and "@graph" in item:
                flattened.extend(item["@graph"])
            else:
                flattened.append(item)
        for obj in flattened:
            if isinstance(obj, dict):
                yield obj


def _business_name_from_page(soup: BeautifulSoup, jsonld_objs: list[dict], fallback: str) -> str:
    for obj in jsonld_objs:
        types = obj.get("@type")
        types = types if isinstance(types, list) else [types]
        if any(t in ("Organization", "LocalBusiness", "Corporation") for t in types if t):
            name = obj.get("name")
            if name and isinstance(name, str):
                return name.strip()
    og = soup.find("meta", property="og:site_name")
    if og and og.get("content"):
        return og["content"].strip()
    if soup.title and soup.title.string:
        parts = re.split(r"[|\-–]", soup.title.string)
        candidate = parts[-1].strip() if len(parts) > 1 else soup.title.string.strip()
        if candidate:
            return candidate
    return fallback


def _address_from_jsonld(jsonld_objs: list[dict]) -> str:
    for obj in jsonld_objs:
        addr = obj.get("address")
        if isinstance(addr, dict):
            parts = [
                addr.get("streetAddress"), addr.get("addressLocality"),
                addr.get("addressRegion"), addr.get("postalCode"),
                addr.get("addressCountry"),
            ]
            joined = ", ".join(p for p in parts if p)
            if joined:
                return joined
        elif isinstance(addr, str) and addr.strip():
            return addr.strip()
    return ""


def _social_links(soup: BeautifulSoup) -> dict:
    links: dict = {}
    for a in soup.find_all("a", href=True):
        href = a["href"]
        netloc = urlparse(href).netloc.lower().replace("www.", "")
        for domain, key in SOCIAL_DOMAINS.items():
            if domain in netloc and key not in links:
                links[key] = href
    return links


def _guess_role(text: str) -> str:
    lowered = text.lower()
    for kw in ROLE_KEYWORDS:
        if kw in lowered:
            return kw.strip().title()
    return ""


def _looks_like_contact_value(line: str) -> bool:
    return "@" in line or bool(re.search(r"\d{3}", line))


def _people_from_page(soup: BeautifulSoup) -> list[Lead]:
    """Heuristic: a mailto/tel link whose nearby text contains a Title-Case
    name is treated as an individual contact (e.g. a staff/team directory).

    Climbs from the link one ancestor at a time (instead of jumping straight
    up a fixed number of levels) and stops as soon as an ancestor's text
    contains a name-shaped line, so it grabs the tightest surrounding
    "card"/row rather than bleeding into unrelated sibling entries.
    """
    people = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        email = phone = ""
        if href.lower().startswith("mailto:"):
            email = href.split(":", 1)[1].split("?")[0].strip()
        elif href.lower().startswith("tel:"):
            phone = href.split(":", 1)[1].strip()
        if not (email or phone):
            continue

        name, role = "", ""
        container = a
        for _ in range(4):
            if container.parent is None:
                break
            container = container.parent
            lines = [ln.strip() for ln in container.get_text("\n", strip=True).split("\n") if ln.strip()]
            for idx, line in enumerate(lines):
                if NAME_RE.match(line):
                    name = line
                    for nxt in lines[idx + 1 : idx + 3]:
                        if not _looks_like_contact_value(nxt):
                            role = nxt
                            break
                    if not role:
                        role = _guess_role(" ".join(lines))
                    break
            if name:
                break

        if name:
            people.append(Lead(contact_name=name, role=role, email=email, phone=phone))
    return people


def _rank_links(soup: BeautifulSoup, base_url: str, root_netloc: str) -> list[str]:
    """Same-domain links whose URL or anchor text looks like a contact/about/
    team page, in document order and de-duplicated."""
    ordered: list[str] = []
    seen_local: set[str] = set()
    for a in soup.find_all("a", href=True):
        link = urljoin(base_url, a["href"]).split("#")[0]
        if not _same_domain(link, root_netloc) or link in seen_local:
            continue
        haystack = f"{link} {a.get_text(' ', strip=True)}".lower()
        if any(kw in haystack for kw in NAV_KEYWORDS):
            seen_local.add(link)
            ordered.append(link)
    return ordered


def extract_leads(
    raw_domain: str,
    config: CrawlConfig | None = None,
    progress_callback=None,
) -> CrawlResult:
    """Crawl `raw_domain` and return the leads found on it."""
    config = config or CrawlConfig()
    domain = normalize_domain(raw_domain)
    result = CrawlResult()

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT, "Accept-Language": "en"})

    base_url, home_resp = _resolve_base_url(session, domain, config.timeout_seconds)
    root_netloc = urlparse(base_url).netloc.lower()
    robots = _get_robot_parser(session, base_url, config.timeout_seconds) if config.respect_robots else None

    business_name = domain
    address = ""
    social_links: dict = {}
    company_emails: set[str] = set()
    company_phones: set[str] = set()
    people_leads: list[Lead] = []

    seen = {base_url}
    queue = [base_url]
    pages_done = 0
    homepage_processed = False

    while queue and pages_done < config.max_pages:
        url = queue.pop(0)

        if robots and not robots.can_fetch(USER_AGENT, url):
            result.warnings.append(f"Skipped (robots.txt disallows): {url}")
            continue

        try:
            resp = home_resp if url == base_url else session.get(url, timeout=config.timeout_seconds)
        except requests.RequestException as exc:
            result.warnings.append(f"Could not fetch {url}: {exc}")
            continue

        pages_done += 1
        if progress_callback:
            progress_callback(pages_done, config.max_pages, url)

        content_type = resp.headers.get("Content-Type", "")
        if resp.status_code >= 400 or "text/html" not in content_type:
            time.sleep(config.delay_seconds)
            continue

        result.pages_crawled.append(url)
        soup = BeautifulSoup(resp.text, "lxml")
        jsonld_objs = list(_extract_jsonld(soup))

        if business_name == domain:
            business_name = _business_name_from_page(soup, jsonld_objs, domain)
        if not address:
            address = _address_from_jsonld(jsonld_objs)
        for key, href in _social_links(soup).items():
            social_links.setdefault(key, href)

        page_text = soup.get_text(" ", strip=True)
        company_emails |= extract_emails(page_text)
        company_phones |= extract_phones(page_text, config.default_region)
        for a in soup.find_all("a", href=True):
            href_lower = a["href"].lower()
            if href_lower.startswith("mailto:"):
                company_emails |= extract_emails(href_lower.split(":", 1)[1])
            elif href_lower.startswith("tel:"):
                company_phones |= extract_phones(href_lower.split(":", 1)[1], config.default_region)

        people_leads.extend(_people_from_page(soup))

        if not homepage_processed:
            homepage_processed = True
            for link in _rank_links(soup, base_url, root_netloc):
                if link not in seen:
                    seen.add(link)
                    queue.append(link)
            if len(queue) < 4:
                for path in FALLBACK_PATHS:
                    link = urljoin(base_url, path)
                    if link not in seen:
                        seen.add(link)
                        queue.append(link)

        time.sleep(config.delay_seconds)

    # Fold business-level fields into every person lead and de-duplicate.
    seen_keys = set()
    for lead in people_leads:
        lead.business_name = business_name
        lead.website = domain
        lead.address = address
        lead.linkedin = social_links.get("linkedin", "")
        lead.twitter = social_links.get("twitter", "")
        lead.facebook = social_links.get("facebook", "")
        lead.instagram = social_links.get("instagram", "")
        key = lead.key()
        if key in seen_keys:
            continue
        seen_keys.add(key)
        result.leads.append(lead)

    used_person_emails = {l.email for l in result.leads if l.email}
    leftover_emails = [e for e in sorted(company_emails) if e not in used_person_emails]

    if leftover_emails or company_phones or not result.leads:
        result.leads.insert(
            0,
            Lead(
                business_name=business_name,
                role="General / Company",
                email=leftover_emails[0] if leftover_emails else "",
                phone=sorted(company_phones)[0] if company_phones else "",
                address=address,
                website=domain,
                linkedin=social_links.get("linkedin", ""),
                twitter=social_links.get("twitter", ""),
                facebook=social_links.get("facebook", ""),
                instagram=social_links.get("instagram", ""),
                source_page=base_url,
            ),
        )

    if not any(l.email or l.phone for l in result.leads):
        result.warnings.append(
            "No public email addresses or phone numbers were found on this domain."
        )

    return result
