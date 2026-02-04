def run():
   import requests
import pandas as pd
from bs4 import BeautifulSoup
import streamlit as st
import os

ARTICLE_ID = st.secrets["ZENDESK_ARTICLE_ID"]
SUBDOMAIN = st.secrets["ZENDESK_SUBDOMAIN"]
EMAIL = st.secrets["ZENDESK_EMAIL"]
TOKEN = st.secrets["ZENDESK_API_TOKEN"]

auth = (f"{EMAIL}/token", TOKEN)

BASE_URL = f"https://{SUBDOMAIN}.zendesk.com/api/v2/help_center/articles/{ARTICLE_ID}"

print("🚀 Zendesk single-article sync started")

# 1️⃣ Fetch article
article_resp = requests.get(f"{BASE_URL}.json", auth=auth)
article = article_resp.json()["article"]

# 2️⃣ Fetch attachments
attach_resp = requests.get(f"{BASE_URL}/attachments.json", auth=auth)
attachments = attach_resp.json().get("article_attachments", [])

os.makedirs("attachments", exist_ok=True)

excel_file = None
pdf_file = None

for att in attachments:
    name = att["file_name"].lower()
    url = att["content_url"]

    file_path = f"attachments/{att['file_name']}"
    with open(file_path, "wb") as f:
        f.write(requests.get(url).content)

    if name.endswith(".xlsx"):
        excel_file = file_path
    elif name.endswith(".pdf"):
        pdf_file = file_path

# 3️⃣ Priority: Excel → PDF → Text
if excel_file:
    print("✅ Using Excel attachment")
    df = pd.read_excel(excel_file)
    df["source"] = "zendesk_excel"

elif pdf_file:
    print("✅ Using PDF attachment")
    import pdfplumber
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"

    df = pd.DataFrame([{
        "content": text,
        "source": "zendesk_pdf"
    }])

else:
    print("✅ Using article text")
    soup = BeautifulSoup(article["body"], "html.parser")
    text = soup.get_text(" ", strip=True)

    df = pd.DataFrame([{
        "content": text,
        "source": "zendesk_text"
    }])

# 4️⃣ Save unified raw file
df.to_excel("offers_from_zendesk_articles.xlsx", index=False)
print("✅ Saved offers_from_zendesk_articles.xlsx")

if __name__ == "__main__":
    run()
