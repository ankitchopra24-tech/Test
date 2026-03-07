import pandas as pd
from datetime import datetime
import re
from io import StringIO

print("🚀 Offer extraction started...")

INPUT_FILE = "zendesk_articles_raw.xlsx"
OUTPUT_FILE = "offers_from_zendesk_articles.xlsx"

# =====================================================
# LOAD ARTICLE
# =====================================================

df = pd.read_excel(INPUT_FILE)

if df.empty:
    raise Exception("❌ No article data found")

html_content = df.iloc[0]["content"]

# =====================================================
# PARSE HTML TABLE
# =====================================================

tables = pd.read_html(StringIO(html_content))

if not tables:
    raise Exception("❌ No tables found in article")

deal_table = tables[0]

# Normalize column names
deal_table.columns = deal_table.columns.str.strip().str.lower()

print("📊 Columns detected:", deal_table.columns.tolist())

offers = []

# =====================================================
# EXTRACT OFFERS
# =====================================================

for _, row in deal_table.iterrows():

    airline = str(row.get("airlines name", "")).strip()
    iata = str(row.get("iata", "")).strip()
    validity = str(row.get("validity", "")).strip()

    cabin_map = {
        "First": row.get("first"),
        "Business": row.get("bus"),
        "Premium Economy": row.get("prem. eco"),
        "Economy": row.get("eco")
    }

    for cabin, deal in cabin_map.items():

        if pd.notna(deal):

            deal_str = str(deal)

            match = re.search(r"\d+(\.\d+)?", deal_str)

            if match:

                percent = float(match.group())

                offers.append({
                    "airline": airline,
                    "iata": iata,
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
    raise Exception("❌ No offers detected")

out_df = out_df.drop_duplicates()

out_df.to_excel(OUTPUT_FILE, index=False)

print(f"✅ Extracted {len(out_df)} offers")
print(f"📄 Saved to {OUTPUT_FILE}")
print("🏁 Offer extraction finished")
