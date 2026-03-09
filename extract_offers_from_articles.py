import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

print("🚀 Offer extraction started...")

INPUT_FILE = "zendesk_articles_raw.xlsx"
OUTPUT_FILE = "offers_from_zendesk_articles.xlsx"

# -----------------------------------
# LOAD ARTICLE
# -----------------------------------

df = pd.read_excel(INPUT_FILE)

if df.empty:
    raise Exception("❌ No article data found")

html = df.iloc[0]["content"]

print("📄 Parsing Zendesk article HTML...")

soup = BeautifulSoup(html, "html.parser")

# -----------------------------------
# FIND ALL ROWS
# -----------------------------------

rows = soup.find_all(["tr","p","div"])

offers = []

for r in rows:

    text = r.get_text(" ", strip=True)

    if "%" not in text:
        continue

    tokens = text.split()

    # detect IATA
    iata = None
    for t in tokens:
        if len(t) == 2 and t.isupper():
            iata = t
            break

    # detect airline name
    airline = None
    if iata:
        idx = tokens.index(iata)
        if idx + 1 < len(tokens):
            airline = tokens[idx + 1]

    # detect percentage
    deal = None
    for t in tokens:
        if "%" in t:
            try:
                deal = float(t.replace("%",""))
            except:
                pass

    if airline and deal:

        offers.append({
            "airline": airline.title(),
            "iata": iata,
            "cabin_class": "Unknown",
            "deal_percent": deal,
            "valid_till": "",
            "source": "Zendesk Article",
            "extracted_on": datetime.now().date().isoformat()
        })

# -----------------------------------
# SAVE OUTPUT
# -----------------------------------

out_df = pd.DataFrame(offers)

if out_df.empty:
    raise Exception("❌ No offers extracted from article")

out_df = out_df.sort_values("deal_percent", ascending=False)
out_df = out_df.drop_duplicates(subset=["iata"])

out_df.to_excel(OUTPUT_FILE, index=False)

print(f"✅ Extracted {len(out_df)} airline offers")
print(f"📄 Saved to {OUTPUT_FILE}")
print("🏁 Offer extraction finished")
