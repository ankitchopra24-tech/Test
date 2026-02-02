print("🚀 Zendesk sync started...")


import requests
import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup

# -------------------------------------------------
# ZENDESK AUTH (READS FROM STREAMLIT SECRETS)
# -------------------------------------------------
ZENDESK_SUBDOMAIN = st.secrets["ZENDESK_SUBDOMAIN"]
ZENDESK_EMAIL = st.secrets["ZENDESK_EMAIL"]
ZENDESK_API_TOKEN = st.secrets["ZENDESK_API_TOKEN"]

auth = (f"{ZENDESK_EMAIL}/token", ZENDESK_API_TOKEN)

# -------------------------------------------------
# FETCH ZENDESK KNOWLEDGE BASE ARTICLES
# -------------------------------------------------
url = f"https://{ZENDESK_SUBDOMAIN}.zendesk.com/api/v2/help_center/articles.json"
response = requests.get(url, auth=auth)

if response.status_code != 200:
    raise Exception(f"Zendesk API failed: {response.status_code}")

articles = response.json().get("articles", [])

rows = []

for article in articles:
    soup = BeautifulSoup(article["body"], "html.parser")
    text = soup.get_text(separator=" ", strip=True)

    rows.append({
        "article_id": article["id"],
        "title": article["title"],
        "content": text,
        "updated_at": article["updated_at"]
    })

df = pd.DataFrame(rows)

# -------------------------------------------------
# SAVE OUTPUT
# -------------------------------------------------
output_file = "zendesk_articles_raw.xlsx"
df.to_excel(output_file, index=False)

print(f"✅ Saved {len(df)} Zendesk articles to {output_file}")

print("✅ Zendesk sync finished successfully")

