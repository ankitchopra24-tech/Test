import streamlit as st
import requests
import pandas as pd
import difflib
from datetime import datetime

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(page_title="Airline Offer Finder Bot", page_icon="✈️")
st.title("✈️ Airline Offer Finder Bot")

# --------------------------------------------------
# ZENDESK AUTH (READ FROM SECRETS)
# --------------------------------------------------
ZENDESK_SUBDOMAIN = st.secrets["ZENDESK_SUBDOMAIN"]
ZENDESK_EMAIL = st.secrets["ZENDESK_EMAIL"]
ZENDESK_API_TOKEN = st.secrets["ZENDESK_API_TOKEN"]

auth = (f"{ZENDESK_EMAIL}/token", ZENDESK_API_TOKEN)

# --------------------------------------------------
# AUTH TEST (SAFE)
# --------------------------------------------------
test_url = f"https://{ZENDESK_SUBDOMAIN}.zendesk.com/api/v2/help_center/articles.json"
resp = requests.get(test_url, auth=auth)

if resp.status_code != 200:
    st.error("❌ Zendesk authentication failed")
    st.stop()
else:
    st.success("✅ Zendesk authentication successful")

# --------------------------------------------------
# LOAD OFFERS (FROM ZENDESK EXTRACTION)
# --------------------------------------------------
OFFERS_FILE = "offers_from_zendesk_articles.xlsx"

try:
    df = pd.read_excel(OFFERS_FILE)
except FileNotFoundError:
    st.error(f"❌ {OFFERS_FILE} not found. Run Zendesk sync first.")
    st.stop()

df.columns = df.columns.str.strip().str.lower()

# Ensure required columns exist
required_cols = [
    "airline", "iata", "cabin_class",
    "deal_percent", "valid_till", "source"
]

for col in required_cols:
    if col not in df.columns:
        df[col] = ""

# --------------------------------------------------
# USER QUERY INPUT (MUST COME FIRST)
# --------------------------------------------------
query = st.text_input("Ask about airline offers (e.g. 'EK business dubai')")

# --------------------------------------------------
# SEARCH + MATCHING LOGIC
# --------------------------------------------------
def match_offer(row, query):
    airline = str(row["airline"]).lower()
    iata = str(row["iata"]).lower()

    if query == iata:
        return True
    if airline in query or query in airline:
        return True
    if iata in query:
        return True
    return False

# --------------------------------------------------
# SEARCH EXECUTION
# --------------------------------------------------
if query:
    query = query.lower().strip()

    results = df[df.apply(lambda r: match_offer(r, query), axis=1)]

    if not results.empty:
        results = results.sort_values(
            by="deal_percent",
            ascending=False
        )

# --------------------------------------------------
# UI RENDERING
# --------------------------------------------------
if query and not results.empty:
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

elif query:
    st.warning("⚠️ No matching offers found")
