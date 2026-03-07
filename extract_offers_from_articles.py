import pandas as pd
import re
from bs4 import BeautifulSoup
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

html = df.iloc[0]["content"]

print("📄 Parsing Zendesk article content...")

soup = BeautifulSoup(html, "html.parser")

# extract all visible text
text = soup.get_text("\n")

lines = [l.strip() for l in text.split("\n") if l.strip()]

offers = []

current_airline = None
current_iata = None

for line in lines:

    # detect airline code
    iata_match = re.fullmatch(r"[A-Z]{2}", line)
    if iata_match:
        current_iata = line
        continue

    # detect airline name (usually uppercase words)
    if line.isupper() and len(line) > 3:
        current_airline = line.title()
        continue

    # detect percentage deals
    deal_match = re.search(r"(\d+(\.\d+)?)\s*%", line)

    if deal_match and current_airline:

        deal = float(deal_match.group(1))

        offers.append({
            "airline": current_airline,
            "iata": current_iata,
            "cabin_class": "Unknown",
            "deal_percent": deal,
            "valid_till": "",
            "source": "Zendesk Article",
            "extracted_on": datetime.now().date().isoformat()
        })

# =====================================================
# CLEAN RESULTS
# =====================================================

out_df = pd.DataFrame(offers)

if out_df.empty:
    raise Exception("❌ No offers extracted")

# keep best deal per airline
out_df = out_df.sort_values("deal_percent", ascending=False)
out_df = out_df.drop_duplicates(subset=["airline","iata"])

# =====================================================
# SAVE
# =====================================================

out_df.to_excel(OUTPUT_FILE, index=False)

print(f"✅ Extracted {len(out_df)} airline offers")
print(f"📄 Saved to {OUTPUT_FILE}")
print("🏁 Offer extraction finished")
