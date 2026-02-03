
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
def find_offer(query):
    query = query.lower()
    results = df.copy()

    if "ek" in query:
        results = results[results["iata"].str.lower() == "ek"]

    if "business" in query:
        results = results[results["cabin_class"].str.contains("business", case=False)]

    if "dubai" in query:
        results = results[results["sector"].str.contains("dubai|uae|middle", case=False)]

    results = results.sort_values(by="deal_%", ascending=False)
    return results.head(3)

# -------------------------------
# UI
# -------------------------------
query = st.text_input("Ask about airline offers")

if query:
    matches = find_offer(query)
    for _, row in matches.iterrows():
        st.markdown(f"""
**✈️ {row['airline']} ({row['iata']})**  
Cabin: {row['cabin_class']}  
Deal: {row['deal_%']}%  
Sector: {row['sector']}  
Valid Till: {row['valid_till']}  
Conditions: {row['key_conditions']}
---
""")
