import pandas as pd
import re
from datetime import datetime

print("🚀 Offer extraction started...")

INPUT_FILE = "zendesk_articles_raw.xlsx"
OUTPUT_FILE = "offers_from_zendesk_articles.xlsx"

# =====================================================
# LOAD ARTICLE
# =====================================================

df = pd.read_excel(INPUT_FILE)

if df.empty:
    raise Exception("❌ No article data found")

content = df.iloc[0]["content"]

print("📄 Parsing article content...")

offers = []

lines = content.split("\n")

for line in lines:

    # Look for airline code + percentage
    percent_match = re.search(r"(\d+(\.\d+)?)\s*%", line)

    if percent_match:

        percent = float(percent_match.group(1))

        # detect airline code
        airline_match = re.search(r"\b[A-Z]{2}\b", line)

        airline_code = airline_match.group(0) if airline_match else ""

        offers.append({
            "airline": airline_code,
            "iata": airline_code,
            "cabin_class": "Unknown",
            "deal_percent": percent,
            "valid_till": "",
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
