import pandas as pd
import re
from datetime import datetime

print("🚀 Offer extraction started...")

INPUT_FILE = "zendesk_articles_raw.xlsx"
OUTPUT_FILE = "offers_from_zendesk_articles.xlsx"

# =====================================================
# LOAD RAW ARTICLE
# =====================================================
df = pd.read_excel(INPUT_FILE)

if df.empty:
    raise Exception("❌ No article data found")

text = df.iloc[0]["content"].lower()

offers = []

# =====================================================
# SIMPLE NLP REGEX (AIRLINE AGNOSTIC)
# =====================================================
airline_pattern = re.compile(
    r"(emirates|air india|air france|klm|delta|lufthansa|qatar|british airways|singapore airlines|[a-z ]+ airlines?)",
    re.IGNORECASE
)

iata_pattern = re.compile(r"\b[A-Z]{2}\b")
deal_pattern = re.compile(r"(\d{1,2})\s?%")
cabin_pattern = re.compile(r"(business|economy|first|premium economy)", re.IGNORECASE)

lines = text.split(". ")

for line in lines:
    airline = airline_pattern.search(line)
    deal = deal_pattern.search(line)

    if airline and deal:
        cabin = cabin_pattern.search(line)
        iata = iata_pattern.search(line.upper())

        offers.append({
            "airline": airline.group(0).title(),
            "iata": iata.group(0) if iata else "",
            "cabin_class": cabin.group(0).title() if cabin else "Any",
            "deal_percent": int(deal.group(1)),
            "valid_till": "",
            "source": "Zendesk Article",
            "extracted_on": datetime.utcnow().date().isoformat()
        })

# =====================================================
# SAVE OUTPUT
# =====================================================
out_df = pd.DataFrame(offers)

if out_df.empty:
    raise Exception("❌ No offers detected in article text")

out_df.to_excel(OUTPUT_FILE, index=False)

print(f"✅ Extracted {len(out_df)} offers")
print(f"📄 Saved to {OUTPUT_FILE}")
print("🏁 Offer extraction finished")
