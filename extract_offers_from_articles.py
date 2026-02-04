import pandas as pd
import re
from datetime import datetime

print("🚀 Offer extraction started")

# =====================================================
# LOAD RAW ARTICLE
# =====================================================
INPUT_FILE = "zendesk_articles_raw.xlsx"
OUTPUT_FILE = "offers_from_zendesk_articles.xlsx"

df = pd.read_excel(INPUT_FILE)

if df.empty:
    raise Exception("❌ zendesk_articles_raw.xlsx is empty")

content = df.iloc[0]["content"].lower()

# =====================================================
# REGEX PATTERNS (GENERIC – ANY AIRLINE)
# =====================================================
AIRLINE_PATTERN = r"(emirates|air india|air france|klm|delta|lufthansa|qatar|british airways|singapore airlines|[a-z ]+ airlines)"
IATA_PATTERN = r"\(([a-z]{2})\)"
CABIN_PATTERN = r"(business|economy|first)"
DEAL_PATTERN = r"(\d{1,2})\s?%"
VALID_PATTERN = r"(valid till|valid until|valid upto)\s+([a-z0-9 ,]+)"

# =====================================================
# EXTRACT OFFERS (LINE BY LINE)
# =====================================================
offers = []

for line in content.split("\n"):
    airline_match = re.search(AIRLINE_PATTERN, line)
    deal_match = re.search(DEAL_PATTERN, line)

    if airline_match and deal_match:
        offers.append({
            "airline": airline_match.group(1).title(),
            "iata": "",
            "cabin_class": "Business" if "business" in line else "Economy",
            "deal_percent": int(deal_match.group(1)),
            "valid_till": "",
            "sector": "",
            "source": "Zendesk Article"
        })

# =====================================================
# SAVE RESULTS
# =====================================================
if not offers:
    raise Exception("❌ No offers extracted from article")

out_df = pd.DataFrame(offers)
out_df.to_excel(OUTPUT_FILE, index=False)

print(f"✅ Extracted {len(out_df)} offers")
print(f"✅ Saved offers to {OUTPUT_FILE}")
print("✅ Offer extraction finished successfully")
