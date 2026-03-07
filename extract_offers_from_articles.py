import pandas as pd
import re
from bs4 import BeautifulSoup
from datetime import datetime

print("🚀 Offer extraction started...")

INPUT_FILE = "zendesk_articles_raw.xlsx"
OUTPUT_FILE = "offers_from_zendesk_articles.xlsx"

df = pd.read_excel(INPUT_FILE)

if df.empty:
    raise Exception("❌ No article data found")

html_content = df.iloc[0]["content"]

# Parse HTML
soup = BeautifulSoup(html_content, "html.parser")

tables = soup.find_all("table")

if not tables:
    raise Exception("❌ No tables found in article")

offers = []

for table in tables:

    df_table = pd.read_html(str(table))[0]

    df_table.columns = df_table.columns.str.strip().str.lower()

    for _, row in df_table.iterrows():

        airline = str(row.get("airlines name", "")).strip()
        iata = str(row.get("iata", "")).strip()

        cabin_map = {
            "First": row.get("first"),
            "Business": row.get("bus"),
            "Premium Economy": row.get("prem. eco"),
            "Economy": row.get("eco")
        }

        for cabin, deal in cabin_map.items():

            if pd.notna(deal) and str(deal).strip() != "" and float(deal) > 0:

                offers.append({
                    "airline": airline,
                    "iata": iata,
                    "cabin_class": cabin,
                    "deal_percent": int(float(deal)),
                    "valid_till": "",
                    "source": "Zendesk Article",
                    "extracted_on": datetime.now().date().isoformat()
                })

out_df = pd.DataFrame(offers)

if out_df.empty:
    raise Exception("❌ No offers detected")

out_df = out_df.drop_duplicates()

out_df.to_excel(OUTPUT_FILE, index=False)

print(f"✅ Extracted {len(out_df)} offers")
print(f"📄 Saved to {OUTPUT_FILE}")
print("🏁 Offer extraction finished")
