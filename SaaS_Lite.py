import streamlit as st
import asyncio
import aiohttp
import re
import pandas as pd
from bs4 import BeautifulSoup
import random
from urllib.parse import quote_plus
import requests

# --- Streamlit Page Setup ---
st.set_page_config(page_title="SaaSquatch Lite", layout="wide")
st.title("SaaSquatch Lite: Enhanced Lead Generation Tool")
st.write("It supports multi-page scraping which includes email IDs and LinkedIn profiles.")

# --- Constants ---
EMAIL_REGEX = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15"
]
FALLBACK_PATHS = ["", "/contact", "/about", "/team"]
GENERIC_EMAILS = ["info@{domain}", "sales@{domain}", "contact@{domain}", "hello@{domain}", "support@{domain}", "admin@{domain}", "office@{domain}"]

# --- Async Fetching Function ---
async def fetch_html(session, url):
    try:
        headers = {'User-Agent': random.choice(USER_AGENTS)}
        async with session.get(url, headers=headers, timeout=15) as resp:
            resp.raise_for_status()
            return await resp.text()
    except:
        return None

# --- LinkedIn Detection ---
async def find_linkedin_on_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    links = set()
    for a in soup.find_all('a', href=True):
        href = a['href']
        if "linkedin.com/company/" in href:
            clean = href.split('?')[0]
            if not clean.startswith("http"):
                clean = "https://" + clean.lstrip("/")
            links.add(clean)
    return sorted(links)[:2]

# --- Google Fallback for LinkedIn ---
def search_linkedin_via_google(domain):
    q = quote_plus(f"site:linkedin.com/company \"{domain}\"")
    url = f"https://www.google.com/search?q={q}"
    hdr = {'User-Agent': random.choice(USER_AGENTS)}
    try:
        resp = requests.get(url, headers=hdr, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        links = set()
        for a in soup.select('a[href]'):
            href = a['href']
            if "linkedin.com/company/" in href:
                clean = href.split("&")[0].replace("/url?q=", "")
                if not clean.startswith("http"):
                    clean = "https://" + clean.lstrip("/")
                links.add(clean)
        return sorted(links)[:2]
    except:
        return []

# --- Lead Score Calculation ---
def calculate_lead_score(row):
    score = 0
    if row['Emails'] != "N/A": score += 1
    if row['LinkedIn Page URL'] != "N/A": score += 1
    if row['Status'] == "Successfully Enriched": score += 1
    return score

# --- Async Lead Enrichment ---
async def enrich(domain):
    result = {
        "Domain": domain,
        "Emails": "N/A",
        "LinkedIn Page URL": "N/A",
        "Status": "Processing..."
    }
    try:
        all_html = []
        async with aiohttp.ClientSession() as session:
            for p in FALLBACK_PATHS:
                for scheme in ("https://", "http://"):
                    html = await fetch_html(session, scheme + domain + p)
                    if html:
                        all_html.append(html)
                        break

        if not all_html:
            result["Status"] = "Failed: Website Unreachable"
            return result

        # Extract Emails from HTML
        emails = set()
        for html in all_html:
            emails |= set(re.findall(EMAIL_REGEX, html))

        # Add generic emails
        for pattern in GENERIC_EMAILS:
            emails.add(pattern.format(domain=domain))

        result["Emails"] = ", ".join(sorted(emails)[:5]) if emails else "N/A"

        # Extract LinkedIn Profiles
        linked = set()
        for html in all_html:
            linked |= set(await find_linkedin_on_html(html))
        if not linked:
            linked = set(search_linkedin_via_google(domain))

        result["LinkedIn Page URL"] = ", ".join(linked) if linked else "N/A"

        # Final status
        result["Status"] = "Successfully Enriched" if (emails or linked) else "Partial"
    except Exception as e:
        result["Status"] = f"Error: {type(e).__name__}"
    return result

# --- Async Main ---
async def main(domains):
    tasks = [enrich(d.strip()) for d in domains if d.strip()]
    return await asyncio.gather(*tasks)

# --- UI Section ---
st.header("1. Enter Company Domains")
with st.form("form"):
    txt = st.text_area("Enter one domain per line (include .com/.in/etc):", height=150)
    go = st.form_submit_button("🔍 Enrich")

if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame()

if go and txt:
    domains = txt.splitlines()
    df = pd.DataFrame(asyncio.run(main(domains)))
    df['Score'] = df.apply(calculate_lead_score, axis=1)
    st.session_state.df = df

# --- Filters & Results ---
if not st.session_state.df.empty:
    df = st.session_state.df
    st.header("2. Filter and Download Results")

    # Filters
    col1, col2, col3 = st.columns(3)
    statuses = df['Status'].unique()
    status_filter = col1.multiselect("Status", statuses, default=statuses)
    has_emails = col2.checkbox("Only Leads with Emails")
    has_linkedin = col3.checkbox("Only Leads with LinkedIn")

    filtered_df = df[df['Status'].isin(status_filter)]
    if has_emails:
        filtered_df = filtered_df[filtered_df['Emails'] != "N/A"]
    if has_linkedin:
        filtered_df = filtered_df[filtered_df['LinkedIn Page URL'] != "N/A"]

    # Global Search
    search = st.text_input("Search in results")
    if search:
        filtered_df = filtered_df[filtered_df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)]

    st.dataframe(filtered_df, use_container_width=True)

    # Download
    st.download_button("Download CSV", filtered_df.to_csv(index=False), "enriched_leads.csv", "text/csv")
else:
    st.info("Submit domain names above to get started.")