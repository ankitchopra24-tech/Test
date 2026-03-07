import os
import sys
import subprocess
import streamlit as st
import requests
import pandas as pd
import difflib
from datetime import datetime

OFFERS_FILE = "offers_from_zendesk_articles.xlsx"
SYNC_MARKER = "last_sync.txt"

# =====================================================
# CONFIG
# =====================================================
ZENDESK_ARTICLE_ID = "25959686732828"
SYNC_MARKER = "last_sync.txt"

# =====================================================
# PAGE CONFIG (FIRST STREAMLIT CALL)
# =====================================================
st.set_page_config(page_title="Airline Offer Finder Bot", page_icon="✈️")
st.title("✈️ Airline Offer Finder Bot")
st.caption(f"📘 Referencing Zendesk Article ID: `{ZENDESK_ARTICLE_ID}`")

# =====================================================
# ZENDESK AUTH (FROM STREAMLIT SECRETS)
# =====================================================
try:
    ZENDESK_SUBDOMAIN = st.secrets["ZENDESK_SUBDOMAIN"]
    ZENDESK_EMAIL = st.secrets["ZENDESK_EMAIL"]
    ZENDESK_API_TOKEN = st.secrets["ZENDESK_API_TOKEN"]
except Exception:
    st.error("❌ Zendesk secrets missing in Streamlit")
    st.stop()

auth = (f"{ZENDESK_EMAIL}/token", ZENDESK_API_TOKEN)

# =====================================================
# AUTH TEST (SAFE)
# =====================================================
test_url = f"https://{ZENDESK_SUBDOMAIN}.zendesk.com/api/v2/help_center/articles/{ZENDESK_ARTICLE_ID}.json"
resp = requests.get(test_url, auth=auth)

if resp.status_code != 200:
    st.error("❌ Zendesk authentication or article access failed")
    st.stop()
else:
    st.success("✅ Zendesk authentication successful")

# =====================================================
# ADMIN ACTIONS
# =====================================================
st.sidebar.markdown("### 🔧 Admin Actions")

if st.sidebar.button("Run Zendesk Sync + Offer Extraction"):
    st.info("🚀 Fetching specific Zendesk article...")

    sync = subprocess.run(
        [
            sys.executable,
            "zendesk_sync.py",
            ZENDESK_ARTICLE_ID,   # 👈 PASS ARTICLE ID
        ],
        capture_output=True,
        text=True
    )

    st.code(sync.stdout or "No output")
    if sync.stderr:
        st.error(sync.stderr)

    st.info("🚀 Extracting offers from article...")

    extract = subprocess.run(
        [
            sys.executable,
            "extract_offers_from_articles.py"
        ],
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
    st.metric("Total Offers Found", len(df))

with c2:
    if os.path.exists(SYNC_MARKER):
        last_sync = open(SYNC_MARKER).read().split("T")[0]
        st.metric("Last Synced", last_sync)
    else:
        st.metric("Last Synced", "Unknown")

# =====================================================
# BUILD DYNAMIC AIRLINE LOOKUP (NO HARD CODING)
# =====================================================
AIRLINE_LOOKUP = {}

for _, row in df.iterrows():
    airline = str(row.get("airline", "")).lower()
    iata = str(row.get("iata", "")).lower()

    if airline:
        AIRLINE_LOOKUP[airline] = airline
    if iata:
        AIRLINE_LOOKUP[iata] = airline

# =====================================================
# SMART NLP SEARCH ENGINE
# =====================================================

def detect_cabin(query):
    q = query.lower()

    if "business" in q or "biz" in q:
        return "business"

    if "economy" in q or "eco" in q:
        return "economy"

    if "first" in q:
        return "first"

    if "premium" in q:
        return "premium economy"

    return None


def detect_airline(query, df):
    q = query.lower()

    for airline in df["airline"].unique():
        if airline.lower() in q:
            return airline

    for code in df["iata"].unique():
        if str(code).lower() in q:
            return code

    return None


def score_offer(row, airline, cabin, query):

    score = 0
    text = f"{row['airline']} {row['iata']} {row['cabin_class']}".lower()

    # Airline match
    if airline:
        if airline.lower() in text:
            score += 4

    # Cabin match
    if cabin:
        if cabin.lower() in row["cabin_class"].lower():
            score += 3

    # Deal boost
    score += float(row["deal_percent"]) / 10

    # Fuzzy similarity
    score += difflib.SequenceMatcher(None, query, text).ratio()

    return score

# =====================================================
# SCORING FUNCTION
# =====================================================
def score_row(row, airline, cabin, query):
    score = 0.0
    text = f"{row['airline']} {row['iata']} {row.get('sector','')}".lower()

    if airline and airline in row["airline"].lower():
        score += 3
    if cabin and cabin in row.get("cabin_class","").lower():
        score += 2

    score += difflib.SequenceMatcher(None, query, text).ratio()
    return score

# =====================================================
# USER QUERY
# =====================================================
query = st.text_input(
    "Ask about airline offers (e.g. 'best business class deal')"
)

if query:

    airline = detect_airline(query, df)
    cabin = detect_cabin(query)

    df["score"] = df.apply(
        lambda r: score_offer(r, airline, cabin, query.lower()),
        axis=1
    )

    results = df.sort_values(
        by=["score", "deal_percent"],
        ascending=False
    )

    results = results.head(20)

    if results.empty:
        st.warning("⚠️ No matching offers found")
        st.stop()

    # =========================
    # BEST OFFER
    # =========================
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

    # =========================
    # ALL MATCHES
    # =========================

    st.markdown("## ✈️ Top Matching Offers")

    for i, row in results.iterrows():

        offer_text = f"""
✈️ {row['airline']} ({row['iata']})
Cabin: {row['cabin_class']}
Deal: {row['deal_percent']}%
Valid Till: {row['valid_till']}
"""

        st.markdown("---")
        st.markdown(f"### ✈️ {row['airline']} ({row['iata']})")

        c1, c2, c3 = st.columns(3)

        c1.write(f"**Cabin**\n{row['cabin_class']}")
        c2.write(f"**Deal**\n{row['deal_percent']}%")
        c3.write(f"**Valid Till**\n{row['valid_till']}")

        st.text_area(
            "📋 Copy offer",
            value=offer_text.strip(),
            height=120,
            key=f"copy_{i}"
        )

# =====================================================
# FOOTER
# =====================================================
st.markdown("---")
st.caption("🤖 Airline Offer Finder Bot • NLP-powered • Single Zendesk Article")
