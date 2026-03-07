import pandas as pd
from bs4 import BeautifulSoup
import re
from datetime import datetime

print("🚀 Offer extraction started...")

INPUT_FILE = "zendesk_articles_raw.xlsx"
OUTPUT_FILE = "offers_from_zendesk_articles.xlsx"

# =====================================================
# LOAD ARTICLE HTML
# =====================================================

df = pd.read_excel(INPUT_FILE)

if df.empty:
    raise Exception("❌ No article data found")

html = df.iloc[0]["content"]

print("📄 Parsing Zendesk article HTML...")

soup = BeautifulSoup(html, "html.parser")

table = soup.find("table")

if table is None:
    raise Exception("❌ No table found in Zendesk article")

rows = table.find_all("tr")

offers = []

# =====================================================
# READ TABLE ROWS
# =====================================================

for row in rows[1:]:  # skip header

    cols = row.find_all("td")

    if len(cols) < 9:
        continue

    airline_code = cols[1].get_text(strip=True)
    airline_name = cols[2].get_text(strip=True)
    iata = cols[3].get_text(strip=True)

    first = cols[4].get_text(strip=True)
    business = cols[5].get_text(strip=True)
    prem_eco = cols[6].get_text(strip=True)
    eco = cols[7].get_text(strip=True)

    validity = cols[8].get_text(strip=True)

    cabin_map = {
        "First": first,
        "Business": business,
        "Premium Economy": prem_eco,
        "Economy": eco
    }

    for cabin, value in cabin_map.items():

        percent_match = re.search(r"\d+(\.\d+)?", value)

        if percent_match:

            percent = float(percent_match.group())

            offers.append({
                "airline": airline_name,
                "iata": airline_code,
                "cabin_class": cabin,
                "deal_percent": percent,
                "valid_till": validity,
                "source": "Zendesk Article",
                "extracted_on": datetime.now().date().isoformat()
            })

# =====================================================
# SAVE RESULTS
# =====================================================

out_df = pd.DataFrame(offers)

if out_df.empty:
    raise Exception("❌ No offers extracted")

out_df = out_df.drop_duplicates()

out_df.to_excel(OUTPUT_FILE, index=False)

print(f"✅ Extracted {len(out_df)} offers")
print(f"📄 Saved to {OUTPUT_FILE}")
print("🏁 Offer extraction finished")
