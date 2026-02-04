import os
import sys
import subprocess
import streamlit as st
import requests
import pandas as pd
import difflib
from datetime import datetime

# =====================================================
# CONFIG
# =====================================================
ZENDESK_ARTICLE_ID = "8747560108444"
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
# NLP PARSER (DYNAMIC)
# =====================================================
def parse_query(query: str):
    query = query.lower()
    airline = cabin = None

    for key, value in AIRLINE_LOOKUP.items():
        if f" {key} " in f" {query} ":
            airline = value
            break

    if any(w in query for w in ["business", "biz", "j"]):
        cabin = "business"
    elif any(w in query for w in ["economy", "eco", "y"]):
        cabin = "economy"

    return airline, cabin

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
    "Ask about airline offers (e.g. 'Best EK business deal')"
)

if query:
    airline, cabin = parse_query(query)

    df["score"] = df.apply(
        lambda r: score_row(r, airline, cabin, query.lower()),
        axis=1
    )

    results = df[df["score"] > 1.2].sort_values(
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
Source: Zendesk Article {ZENDESK_ARTICLE_ID}
"""

        st.markdown("---")
        st.markdown(f"### ✈️ {row['airline']} ({row['iata']})")

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
st.caption("🤖 Airline Offer Finder Bot • NLP-powered • Single Zendesk Article")
