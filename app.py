import os
import sys
import subprocess
import streamlit as st
import requests
import pandas as pd
import difflib
from datetime import datetime

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(page_title="Airline Offer Finder Bot", page_icon="✈️")
st.title("✈️ Airline Offer Finder Bot")

# =====================================================
# ZENDESK AUTH
# =====================================================
try:
    ZENDESK_SUBDOMAIN = st.secrets["ZENDESK_SUBDOMAIN"]
    ZENDESK_EMAIL = st.secrets["ZENDESK_EMAIL"]
    ZENDESK_API_TOKEN = st.secrets["ZENDESK_API_TOKEN"]
except Exception:
    st.error("❌ Zendesk secrets missing in Streamlit")
    st.stop()

auth = (f"{ZENDESK_EMAIL}/token", ZENDESK_API_TOKEN)

test_url = f"https://{ZENDESK_SUBDOMAIN}.zendesk.com/api/v2/help_center/articles.json"
resp = requests.get(test_url, auth=auth)

if resp.status_code != 200:
    st.error("❌ Zendesk authentication failed")
    st.stop()
else:
    st.success("✅ Zendesk authentication successful")

# =====================================================
# FILE PATHS
# =====================================================
OFFERS_FILE = "offers_from_zendesk_articles.xlsx"
SYNC_MARKER = "last_sync.txt"

# =====================================================
# ADMIN ACTIONS
# =====================================================
st.sidebar.markdown("### 🔧 Admin Actions")

if st.sidebar.button("Run Zendesk Sync + Offer Extraction"):
    st.info("🚀 Running Zendesk sync...")

    sync = subprocess.run(
        [sys.executable, "zendesk_sync.py"],
        capture_output=True,
        text=True
    )
    st.code(sync.stdout or "No output")
    if sync.stderr:
        st.error(sync.stderr)

    st.info("🚀 Running offer extraction...")

    extract = subprocess.run(
        [sys.executable, "extract_offers_from_articles.py"],
        capture_output=True,
        text=True
    )
    st.code(extract.stdout or "No output")
    if extract.stderr:
        st.error(extract.stderr)

    with open(SYNC_MARKER, "w") as f:
        f.write(datetime.utcnow().isoformat())

    st.success("✅ Sync & extraction completed")

# =====================================================
# LOAD OFFERS
# =====================================================
if not os.path.exists(OFFERS_FILE):
    st.warning("⚠️ No offers file found. Run Zendesk sync from the sidebar.")
    st.stop()

df = pd.read_excel(OFFERS_FILE)

if df.empty:
    st.warning("⚠️ Offers file is empty.")
    st.stop()

df.columns = df.columns.str.strip().str.lower()

# =====================================================
# HEADER STATS
# =====================================================
st.markdown("### 📊 Offer Snapshot")
c1, c2 = st.columns(2)

with c1:
    st.metric("Total Active Offers", len(df))

with c2:
    if os.path.exists(SYNC_MARKER):
        last_sync = open(SYNC_MARKER).read().strip()
        st.metric("Last Updated", last_sync.split("T")[0])
    else:
        st.metric("Last Updated", "Unknown")

# =====================================================
# DYNAMIC NLP CONFIG (NO HARD-CODED AIRLINES)
# =====================================================
CABIN_SYNONYMS = {
    "business": ["business", "biz", "j"],
    "economy": ["economy", "eco", "y"],
    "first": ["first", "f"]
}

LOCATIONS = [
    "dubai", "uae", "india", "usa", "america",
    "europe", "london", "paris", "bangkok",
    "singapore", "sydney"
]

# Build airline lookup dynamically from data
AIRLINE_LOOKUP = {}

for _, r in df.iterrows():
    airline = str(r.get("airline", "")).lower().strip()
    iata = str(r.get("iata", "")).lower().strip()

    if airline:
        AIRLINE_LOOKUP[airline] = airline
    if iata:
        AIRLINE_LOOKUP[iata] = airline

# =====================================================
# NLP PARSER (DYNAMIC)
# =====================================================
def parse_query_nlp(query: str):
    q = query.lower()
    airline = cabin = location = None

    # Airline / IATA detection
    for key, value in AIRLINE_LOOKUP.items():
        if f" {key} " in f" {q} ":
            airline = value
            break

    # Cabin detection
    for c, words in CABIN_SYNONYMS.items():
        if any(w in q for w in words):
            cabin = c
            break

    # Location detection
    for loc in LOCATIONS:
        if loc in q:
            location = loc
            break

    return airline, cabin, location

# =====================================================
# NLP MATCH SCORING
# =====================================================
def score_row(row, airline, cabin, location, query):
    score = 0.0
    text = f"{row.get('airline','')} {row.get('iata','')} {row.get('cabin_class','')} {row.get('sector','')}".lower()

    if airline and airline in row.get("airline", "").lower():
        score += 3
    if cabin and cabin in row.get("cabin_class", "").lower():
        score += 2
    if location and location in text:
        score += 1

    score += difflib.SequenceMatcher(None, query, text).ratio()
    return score

# =====================================================
# USER QUERY
# =====================================================
query = st.text_input("Ask about airline offers (e.g. 'Best EK business deal to Dubai')")

if query:
    airline, cabin, location = parse_query_nlp(query)

    df["score"] = df.apply(
        lambda r: score_row(r, airline, cabin, location, query.lower()),
        axis=1
    )

    results = df[df["score"] > 1.5].sort_values(
        by=["score", "deal_percent"],
        ascending=False
    )

    if results.empty:
        st.warning("⚠️ No matching offers found")
        st.stop()

    # =================================================
    # BEST OFFER
    # =================================================
    best = results.iloc[0]
    st.markdown("## 🏆 Best Available Offer")
    st.success(
        f"""
✈️ **{best['airline']} ({best['iata']})**  
Cabin: **{best['cabin_class']}**  
Deal: **{best['deal_percent']}%**  
Valid Till: **{best['valid_till']}**
"""
    )

    # =================================================
    # ALL RESULTS
    # =================================================
    st.markdown("## ✈️ All Matching Offers")

    for i, row in results.iterrows():
        offer_text = f"""
✈️ {row['airline']} ({row['iata']})
Cabin: {row['cabin_class']}
Deal: {row['deal_percent']}%
Valid Till: {row['valid_till']}
Source: {row.get('source','Zendesk')}
"""

        st.markdown("---")
        st.markdown(f"### ✈️ {row['airline']} ({row['iata']})")

        c1, c2, c3 = st.columns(3)
        c1.write(f"**Cabin**\n{row['cabin_class']}")
        c2.write(f"**Deal**\n{row['deal_percent']}%")
        c3.write(f"**Valid Till**\n{row['valid_till']}")

        st.text_area(
            "📋 Copy offer details",
            value=offer_text.strip(),
            height=120,
            key=f"copy_{i}"
        )

# =====================================================
# FOOTER
# =====================================================
st.markdown("---")
st.caption("🤖 Airline Offer Finder Bot • Dynamic NLP • Zendesk Knowledge Base")
