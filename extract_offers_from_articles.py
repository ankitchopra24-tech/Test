import pandas as pd
from datetime import datetime
import re
from io import StringIO

print("🚀 Offer extraction started...")

INPUT_FILE = "zendesk_articles_raw.xlsx"
OUTPUT_FILE = "offers_from_zendesk_articles.xlsx"

# =====================================================
# LOAD ARTICLE HTML
# =====================================================

df = pd.read_excel(INPUT_FILE)

if df.empty:
    raise Exception("❌ No article data found")

html_content = df.iloc[0]["content"]

print("📄 Reading HTML table from article...")

# Parse table
tables = pd.read_html(StringIO(html_content))

if not tables:
    raise Exception("❌ No tables found in article")

deal_table = tables[0]

# Normalize column names
deal_table.columns = deal_table.columns.str.strip().str.lower()

print("📊 Columns detected:", deal_table.columns.tolist())

offers = []

# =====================================================
# CONVERT TABLE ROWS TO OFFERS
# =====================================================

for _, row in deal_table.iterrows():

    airline_name = str(row.get("airlines name", "")).strip()
    iata = str(row.get("iata", "")).strip()
    validity = str(row.get("validity", "")).strip()

    cabin_columns = {
        "First": row.get("first"),
        "Business": row.get("bus"),
        "Premium Economy": row.get("prem. eco"),
        "Economy": row.get("eco")
    }

    for cabin, value in cabin_columns.items():

        if pd.notna(value):

            value_str = str(value)

            percent_match = re.search(r"\d+(\.\d+)?", value_str)

            if percent_match:

                percent = float(percent_match.group())

                offers.append({
                    "airline": airline_name,
                    "iata": iata,
                    "cabin_class": cabin,
                    "deal_percent": percent,
                    "valid_till": validity,
                    "source": "Zendesk Article",
                    "extracted_on": datetime.now().date().isoformat()
                })

# =====================================================
# SAVE OUTPUT
# =====================================================

out_df = pd.DataFrame(offers)

if out_df.empty:
    raise Exception("❌ No offers detected")

out_df = out_df.drop_duplicates()

out_df.to_excel(OUTPUT_FILE, index=False)

print(f"✅ Extracted {len(out_df)} offers")
print(f"📄 Saved to {OUTPUT_FILE}")
print("🏁 Offer extraction finished")
