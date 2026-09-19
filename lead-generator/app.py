"""Website Lead Generator -- Streamlit frontend.

Takes a company's website domain, crawls its own public pages (home,
contact, about, team, ...), and compiles whatever business name, people,
emails, phone numbers, address and social profiles it can find into a
downloadable leads table. See backend/extractor.py for the crawl logic.
"""
from __future__ import annotations

import io
import time

import pandas as pd
import streamlit as st

from backend.extractor import CrawlConfig, extract_leads

st.set_page_config(page_title="Lead Generator", page_icon="🎯", layout="wide")

st.markdown(
    """
    <style>
      .block-container { padding-top: 2.2rem; }
      div[data-testid="stMetric"] {
          background-color: #161B22;
          border: 1px solid #262C36;
          border-radius: 10px;
          padding: 12px 16px;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🎯 Website Lead Generator")
st.caption(
    "Enter a company's website domain to pull its publicly listed business "
    "name, contacts, emails, phone numbers, address and social profiles "
    "into a ready-to-export lead sheet."
)

with st.sidebar:
    st.header("Crawl settings")
    max_pages = st.slider("Max pages to crawl", min_value=3, max_value=40, value=15)
    delay = st.slider("Delay between requests (seconds)", 0.0, 3.0, 0.5, 0.1)
    respect_robots = st.checkbox(
        "Respect robots.txt", value=True,
        help="Recommended: skip pages the site's robots.txt disallows.",
    )
    default_region = st.selectbox(
        "Default phone region",
        ["US", "GB", "IN", "CA", "AU", "DE", "FR", "SG", "AE"],
        index=0,
        help="Used only for phone numbers on the page that don't include a country code.",
    )
    st.divider()
    st.caption(
        "This tool only reads publicly published pages on the domain you "
        "enter (home / contact / about / team) -- it never logs in "
        "anywhere and never queries third-party directories."
    )

if "history" not in st.session_state:
    st.session_state.history = []

domain_input = st.text_input("Website domain", placeholder="e.g. acmecorp.com")
run = st.button("Extract leads", type="primary")

if run:
    if not domain_input.strip():
        st.error("Please enter a domain first.")
    else:
        config = CrawlConfig(
            max_pages=max_pages,
            delay_seconds=delay,
            respect_robots=respect_robots,
            default_region=default_region,
        )
        progress = st.progress(0.0, text="Starting crawl...")

        def _on_progress(done: int, total: int, url: str) -> None:
            progress.progress(min(done / total, 1.0), text=f"Crawled {done}/{total}: {url}")

        try:
            result = extract_leads(domain_input, config, progress_callback=_on_progress)
        except ValueError as exc:
            progress.empty()
            st.error(str(exc))
        except ConnectionError as exc:
            progress.empty()
            st.error(str(exc))
        except Exception as exc:  # noqa: BLE001 - surface any unexpected crawl failure to the user
            progress.empty()
            st.error(f"Unexpected error while crawling this domain: {exc}")
        else:
            progress.empty()
            rows = [lead.__dict__ for lead in result.leads]
            df = pd.DataFrame(rows)

            if df.empty:
                st.warning("No leads could be extracted from this domain.")
            else:
                col1, col2 = st.columns(2)
                col1.metric("Leads found", len(df))
                col2.metric("Pages crawled", len(result.pages_crawled))

                st.dataframe(df, use_container_width=True, hide_index=True)

                csv_bytes = df.to_csv(index=False).encode("utf-8")
                excel_buffer = io.BytesIO()
                with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
                    df.to_excel(writer, index=False, sheet_name="Leads")

                dl1, dl2 = st.columns(2)
                dl1.download_button(
                    "Download CSV", csv_bytes,
                    file_name=f"{domain_input.strip()}_leads.csv", mime="text/csv",
                )
                dl2.download_button(
                    "Download Excel", excel_buffer.getvalue(),
                    file_name=f"{domain_input.strip()}_leads.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )

                st.session_state.history.insert(0, {
                    "domain": domain_input.strip(),
                    "leads": len(df),
                    "pages": len(result.pages_crawled),
                    "time": time.strftime("%H:%M:%S"),
                })

            if result.warnings:
                with st.expander(f"Crawl notes ({len(result.warnings)})"):
                    for warning in result.warnings:
                        st.write("- " + warning)

if st.session_state.history:
    st.divider()
    st.subheader("Recent extractions")
    st.table(pd.DataFrame(st.session_state.history))
