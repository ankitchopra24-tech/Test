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

text_blocks = soup.get_text("\n")

lines = [l.strip() for l in text_blocks.split("\n") if l.strip()]

offers = []

current_airline = None
current_iata = None

# =====================================================
# DETECT AIRLINE ROWS
# =====================================================

for line in lines:

    # detect airline code
    airline_match = re.search(r"\b[A-Z]{2}\b", line)

    if airline_match:
        current_iata = airline_match.group()

    # detect airline name
    if len(line.split()) > 1 and not "%" in line and line.isupper():
        current_airline = line

    # detect percentage
    percent_match = re.search(r"(\d+(\.\d+)?)\s*%", line)

    if percent_match and current_airline:

        percent = float(percent_match.group(1))

        offers.append({
            "airline": current_airline,
            "iata": current_iata,
            "cabin_class": "Unknown",
            "deal_percent": percent,
            "valid_till": "",
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
