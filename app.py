import streamlit as st
import requests
import pandas as pd
import os
import sys
import subprocess
from datetime import datetime, timedelta

# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(page_title="Airline Offer Finder Bot", page_icon="✈️")
st.title("✈️ Airline Offer Finder Bot")

# ==================================================
# ZENDESK AUTH (FROM SECRETS)
# ==================================================
ZENDESK_SUBDOMAIN = st.secrets["ZENDESK_SUBDOMAIN"]
ZENDESK_EMAIL = st.secrets["ZENDESK_EMAIL"]
ZENDESK_API_TOKEN = st.secrets["ZENDESK_API_TOKEN"]

auth = (f"{ZENDESK_EMAIL}/token", ZENDESK_API_TOKEN)

# ==================================================
# AUTH CHECK
# ==================================================
test_url = f"https://{ZENDESK_SUBDOMAIN}.zendesk.com/api/v2/help_center/articles.json"
resp = requests.get(test_url, auth=auth)

if resp.status_code != 200:
    st.error("❌ Zendesk authentication failed")
    st.stop()
else:
    st.success("✅ Zendesk authentication successful")

# ==================================================
# AUTO DAILY SYNC (OPTION 5)
# ==================================================
OFFERS_FILE = "offers_from_zendesk_articles.xlsx"
SYNC_MARKER = "last_sync.txt"
SYNC_INTERVAL_HOURS = 24

def needs_sync():
    if not os.path.exists(OFFERS_FILE):
        return True
    if not os.path.exists(SYNC_MARKER):
        return True

    last_sync = datetime.fromisoformat(
        open(SYNC_MARKER).read().strip()
    )
    return datetime.utcnow() - last_sync > timedelta(hours=SYNC_INTERVAL_HOURS)

if needs_sync():
    with st.spinner("🔄 Syncing latest offers from Zendesk..."):
        subprocess.run(
            [sys.executable, "zendesk_sync.py"],
            check=True
        )
        subprocess.run(
            [sys.executable, "extract_offers_from_articles.py"],
            check=True
        )

        with open(SYNC_MARKER, "w") as f:
            f.write(datetime.utcnow().isoformat())

# ==================================================
# LOAD OFFERS
# ==================================================
df = pd.read_excel(OFFERS_FILE)
df.columns = df.columns.str.strip().str.lower()

required_cols = [
    "airline", "iata", "cabin_class",
    "deal_percent", "valid_till", "source"
]

for col in required_cols:
    if col not in df.columns:
        df[col] = ""

# ==================================================
# USER QUERY INPUT
# ==================================================
query = st.text_input(
    "Ask about airline offers (e.g. 'EK business dubai', 'best AI economy')"
)

# ==================================================
# SEARCH LOGIC
# ==================================================
def match_offer(row, q):
    airline = str(row["airline"]).lower()
    iata = str(row["iata"]).lower()

    if q == iata:
        return True
    if airline in q or q in airline:
        return True
    if iata in q:
        return True
    return False

# ==================================================
# SEARCH + UI
# ==================================================
if query:
    q = query.lower().strip()
    results = df[df.apply(lambda r: match_offer(r, q), axis=1)]

    if not results.empty:
        results = results.sort_values(
            by="deal_percent",
            ascending=False
        )

        for i, row in results.iterrows():
            offer_text = f"""
✈️ {row['airline']} ({row['iata']})
Cabin: {row['cabin_class']}
Deal: {row['deal_percent']}%
Valid Till: {row['valid_till']}
Source: {row['source']}
"""

            st.markdown("### ✈️ Offer")
            st.text(offer_text.strip())

            # COPY BOX
            st.text_area(
                "Copy this offer",
                value=offer_text.strip(),
                height=140,
                key=f"copy_{i}"
            )
    else:
        st.warning("⚠️ No matching offers found")
