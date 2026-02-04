def run():
    print("🚀 Zendesk sync started...")

    import requests
    import pandas as pd
    from bs4 import BeautifulSoup
    import streamlit as st

    ZENDESK_SUBDOMAIN = st.secrets["ZENDESK_SUBDOMAIN"]
    ZENDESK_EMAIL = st.secrets["ZENDESK_EMAIL"]
    ZENDESK_API_TOKEN = st.secrets["ZENDESK_API_TOKEN"]

    auth = (f"{ZENDESK_EMAIL}/token", ZENDESK_API_TOKEN)

    url = f"https://{ZENDESK_SUBDOMAIN}.zendesk.com/api/v2/help_center/articles.json"
    response = requests.get(url, auth=auth)

    if response.status_code != 200:
        raise Exception(f"Zendesk API failed: {response.status_code}")

    articles = response.json().get("articles", [])

    rows = []
    for article in articles:
        soup = BeautifulSoup(article["body"], "html.parser")
        rows.append({
            "article_id": article["id"],
            "title": article["title"],
            "content": soup.get_text(" ", strip=True),
            "updated_at": article["updated_at"]
        })

    df = pd.DataFrame(rows)
    df.to_excel("zendesk_articles_raw.xlsx", index=False)

    print(f"✅ Saved {len(df)} Zendesk articles to zendesk_articles_raw.xlsx")
    print("✅ Zendesk sync finished successfully")


if __name__ == "__main__":
    run()
