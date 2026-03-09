import pandas as pd
import re
from bs4 import BeautifulSoup
from datetime import datetime

print("🚀 Offer extraction started...")

INPUT_FILE = "zendesk_articles_raw.xlsx"
OUTPUT_FILE = "offers_from_zendesk_articles.xlsx"

# -------------------------------------------------
# Load article HTML
# -------------------------------------------------

df = pd.read_excel(INPUT_FILE)

if df.empty:
    raise Exception("❌ No article data found")

html = df.iloc[0]["content"]

print("📄 Parsing Zendesk article content...")

soup = BeautifulSoup(html, "html.parser")

text = soup.get_text("\n")

lines = [l.strip() for l in text.split("\n") if l.strip()]

offers = []

current_iata = None
current_airline = None

# -------------------------------------------------
# Extract rows
# -------------------------------------------------

for line in lines:

    # detect IATA (AA, JL, QR etc.)
    iata_match = re.fullmatch(r"[A-Z]{2}", line)
    if iata_match:
        current_iata = line
        continue

    # detect airline name
    if current_iata and not "%" in line and len(line.split()) <= 3:
        current_airline = line.title()
        continue

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

# -------------------------------------------------
# Final dataset
# -------------------------------------------------

out_df = pd.DataFrame(offers)

if out_df.empty:
    raise Exception("❌ No offers extracted")

out_df = out_df.sort_values("deal_percent", ascending=False)
out_df = out_df.drop_duplicates(subset=["airline", "iata"])

out_df.to_excel(OUTPUT_FILE, index=False)

print(f"✅ Extracted {len(out_df)} offers")
print(f"📄 Saved to {OUTPUT_FILE}")
print("🏁 Offer extraction finished")
