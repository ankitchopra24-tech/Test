import sys
import requests
import pandas as pd
import streamlit as st
from bs4 import BeautifulSoup

# =====================================================
# READ ARTICLE ID FROM CLI
# =====================================================
if len(sys.argv) < 2:
    raise Exception("❌ Article ID not provided to zendesk_sync.py")

ARTICLE_ID = sys.argv[1]

print(f"🚀 Zendesk sync started for article {ARTICLE_ID}")

# =====================================================
# AUTH FROM STREAMLIT SECRETS
# =====================================================
ZENDESK_SUBDOMAIN = st.secrets["ZENDESK_SUBDOMAIN"]
ZENDESK_EMAIL = st.secrets["ZENDESK_EMAIL"]
ZENDESK_API_TOKEN = st.secrets["ZENDESK_API_TOKEN"]

auth = (f"{ZENDESK_EMAIL}/token", ZENDESK_API_TOKEN)

# =====================================================
# FETCH ARTICLE
# =====================================================
url = f"https://{ZENDESK_SUBDOMAIN}.zendesk.com/api/v2/help_center/articles/{ARTICLE_ID}.json"
resp = requests.get(url, auth=auth)

if resp.status_code != 200:
    raise Exception(f"❌ Failed to fetch article {ARTICLE_ID}")

article = resp.json()["article"]

# =====================================================
# CLEAN HTML CONTENT
# =====================================================
soup = BeautifulSoup(article["body"], "html.parser")
text_content = soup.get_text(separator=" ", strip=True)

# =====================================================
# SAVE TO EXCEL
# =====================================================
df = pd.DataFrame([
    {
        "article_id": article["id"],
        "title": article["title"],
        "content": text_content,
        "updated_at": article["updated_at"],
        "source": "Zendesk"
    }
])

output_file = "zendesk_articles_raw.xlsx"
df.to_excel(output_file, index=False)

print(f"✅ Saved article to {output_file}")
print("✅ Zendesk sync finished successfully")
