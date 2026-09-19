# 🎯 Website Lead Generator

A Streamlit app that takes a company's **website domain** and compiles a
table of leads from what that site publishes about itself: business name,
staff/contact names and roles, emails, phone numbers, postal address, and
social profiles. Results are shown in a table and can be downloaded as
CSV or Excel.

This is a standalone tool inside the VoteCast repo — it is unrelated to the
`civic-journey` app also in this repo and lives entirely in this folder.

## How it works (scope & ethics)

Given `acmecorp.com`, the backend (`backend/extractor.py`):

1. Fetches the homepage, then follows same-domain links whose text/URL
   looks like a contact/about/team page (falling back to a short list of
   common guesses like `/contact`, `/about`, `/team` if none are found).
2. Reads structured data (`schema.org` JSON-LD), meta tags, `mailto:`/`tel:`
   links, and visible text to pull out the business name, address, social
   links, and any named people with an email/phone near their name.
3. Compiles everything into one row per person found, plus a fallback
   "General / Company" row with the business's own main contact details.

It **only** ever visits pages on the domain you type in — it never signs
into LinkedIn, Google, or any other service, and never scrapes third-party
directories. It is polite by design: it honours `robots.txt` (toggle in the
sidebar), sends a descriptive User-Agent, rate-limits itself between
requests, and caps how many pages it will fetch per run. Only crawl domains
you're authorized to crawl (your own company's site, a client's, or a
prospect's public site as part of legitimate sales research) and respect
each site's terms of use.

There are no logins or API keys required to run this app — it works purely
by reading a site's own public pages.

## Run it locally

```bash
cd lead-generator
pip install -r requirements.txt
streamlit run app.py
```

Open the URL Streamlit prints (typically `http://localhost:8501`).

## Run the tests

```bash
cd lead-generator
pip install -r requirements.txt pytest
python -m pytest tests/ -v
```

The tests mock all HTTP calls against an in-memory fake company website, so
they run offline and don't depend on any real site staying reachable.

## Deploying to Streamlit Community Cloud (get a public link)

Streamlit's free hosting is tied to **your own** GitHub + Streamlit account
— an AI agent has no way to sign in on your behalf (and shouldn't be asked
to: never share passwords or account credentials with any assistant). The
steps below take about two minutes and require nothing more than clicking
"Deploy" while logged into your own accounts:

1. Push this branch to GitHub (already done if you're reading this from the
   repo) — the app lives at `lead-generator/app.py` on this repo.
2. Go to **[share.streamlit.io](https://share.streamlit.io)** and sign in
   with your GitHub account (the same one that owns/forked this repo).
3. Click **"New app"** → **"Deploy a public app from GitHub"** and fill in:
   - **Repository**: `bajpaishivanshu67-sudo/VoteCast`
   - **Branch**: `claude/charming-goodall-9bqm2h` (or `main` after merging)
   - **Main file path**: `lead-generator/app.py`
4. Click **Deploy**. Streamlit Cloud installs `lead-generator/requirements.txt`
   automatically and gives you a live `https://<your-app-name>.streamlit.app`
   URL a minute or two later — that's the link to share.

No further sign-in is needed inside the app itself; it has no user accounts
and no secrets to configure. If you'd rather host it elsewhere (Render,
Railway, a VM, etc.), any host that can run `streamlit run app.py` from the
`lead-generator/` folder with its `requirements.txt` works the same way.

## Project layout

```
lead-generator/
  app.py                  # Streamlit UI
  backend/
    models.py             # Lead dataclass
    validators.py         # domain/email/phone parsing & filtering
    extractor.py           # the crawler itself
  tests/test_extractor.py # offline unit + integration tests
  requirements.txt
```
