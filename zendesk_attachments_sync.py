import requests
import streamlit as st
import pandas as pd
import os

# -----------------------------
# ZENDESK AUTH
# -----------------------------
ZENDESK_SUBDOMAIN = st.secrets["ZENDESK_SUBDOMAIN"]
ZENDESK_EMAIL = st.secrets["ZENDESK_EMAIL"]
ZENDESK_API_TOKEN = st.secrets["ZENDESK_API_TOKEN"]

auth = (f"{ZENDESK_EMAIL}/token", ZENDESK_API_TOKEN)

ATTACH_DIR = "zendesk_attachments"
os.makedirs(ATTACH_DIR, exist_ok=True)

# -----------------------------
# FETCH ARTICLES WITH ATTACHMENTS
# -----------------------------
url = f"https://{ZENDESK_SUBDOMAIN}.zendesk.com/api/v2/help_center/articles.json"
articles = requests.get(url, auth=auth).json()["articles"]

downloaded = []

for article in articles:
    article_id = article["id"]
    attach_url = f"https://{ZENDESK_SUBDOMAIN}.zendesk.com/api/v2/help_center/articles/{article_id}/attachments.json"

    res = requests.get(attach_url, auth=auth)
    if res.status_code != 200:
        continue

    for att in res.json().get("article_attachments", []):
        file_url = att["content_url"]
        file_name = f"{ATTACH_DIR}/{att['file_name']}"

        file_data = requests.get(file_url).content
        with open(file_name, "wb") as f:
            f.write(file_data)

        downloaded.append({
            "article_id": article_id,
            "file_name": att["file_name"],
            "file_path": file_name
        })

df = pd.DataFrame(downloaded)
df.to_excel("zendesk_attachments_index.xlsx", index=False)

print(f"✅ Downloaded {len(df)} attachments")
