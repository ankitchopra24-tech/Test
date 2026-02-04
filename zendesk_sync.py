import requests
import pandas as pd
import streamlit as st
from bs4 import BeautifulSoup

print("🚀 Zendesk sync started...")

# =====================================================
# CONFIG
# =====================================================
ZENDESK_ARTICLE_ID = "8747560108444"

ZENDESK_SUBDOMAIN = st.secrets["ZENDESK_SUBDOMAIN"]
ZENDESK_EMAIL = st.secrets["ZENDESK_EMAIL"]
ZENDESK_API_TOKEN = st.secrets["ZENDESK_API_TOKEN"]

auth = (f"{ZENDESK_EMAIL}/token", ZENDESK_API_TOKEN)

# =====================================================
# FETCH SINGLE ARTICLE
# =====================================================
url = f"https://{ZENDESK_SUBDOMAIN}.zendesk.com/api/v2/help_center/articles/{ZENDESK_ARTICLE_ID}.json"

response = requests.get(url, auth=auth)

if response.status_code != 200:
    raise Exception(
        f"❌ Failed to fetch article {ZENDESK_ARTICLE_ID}. "
        f"Status: {response.status_code} | {response.text}"
    )

article = response.json()["article"]

# =====================================================
# CLEAN HTML → TEXT
# =====================================================
soup = BeautifulSoup(article["body"], "html.parser")
text = soup.get_text(separator=" ", strip=True)

# =====================================================
# SAVE TO EXCEL
# =====================================================
df = pd.DataFrame([{
    "article_id": article["id"],
    "title": article["title"],
    "content": text,
    "updated_at": article["updated_at"]
}])

output_file = "zendesk_articles_raw.xlsx"
df.to_excel(output_file, index=False)

print(f"✅ Saved article {article['id']} to {output_file}")
print("🏁 Zendesk sync finished successfully")
