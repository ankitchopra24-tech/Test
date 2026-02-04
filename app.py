

import streamlit as st
import requests
import pandas as pd
import difflib

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(page_title="Airline Offer Finder Bot", page_icon="✈️")
st.title("✈️ Airline Offer Finder Bot")

# -------------------------------
# ZENDESK AUTH (READ FROM SECRETS)
# -------------------------------
USE_ZENDESK = True  # keep True

ZENDESK_SUBDOMAIN = st.secrets["ZENDESK_SUBDOMAIN"]
ZENDESK_EMAIL = st.secrets["ZENDESK_EMAIL"]
ZENDESK_API_TOKEN = st.secrets["ZENDESK_API_TOKEN"]

auth = (f"{ZENDESK_EMAIL}/token", ZENDESK_API_TOKEN)

# -------------------------------
# OPTIONAL: AUTH TEST
# -------------------------------
test_url = f"https://{ZENDESK_SUBDOMAIN}.zendesk.com/api/v2/help_center/articles.json"
resp = requests.get(test_url, auth=auth)

if resp.status_code != 200:
    st.error("❌ Zendesk authentication failed")
    st.stop()
else:
    st.success("✅ Zendesk authentication successful")

# -------------------------------
# LOAD OFFERS
# -------------------------------
df = pd.read_excel("sample_offers.xlsx")
df.columns = df.columns.str.strip().str.lower()

col_map = {
    "airline": "airline",
    "iata": "iata",
    "cabin": "cabin_class",
    "deal": "deal_%",
    "sector": "sector",
    "valid": "valid_till",
    "conditions": "key_conditions"
}

# -------------------------------
# SEARCH FUNCTION
# -------------------------------
if query:
    query = query.lower().strip()

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

    results = df[df.apply(lambda r: match_offer(r, query), axis=1)]
    results = results.sort_values(by="deal_percent", ascending=False)


# -------------------------------
# UI
# -------------------------------
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

    # 👇 COPY BUTTON (UI)
    st.text_area(
        "Copy this offer",
        value=offer_text.strip(),
        height=140,
        key=f"copy_{i}"
    )

