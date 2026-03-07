import pandas as pd
from datetime import datetime

print("🚀 Offer extraction started...")

INPUT_FILE = "zendesk_articles_raw.xlsx"
OUTPUT_FILE = "offers_from_zendesk_articles.xlsx"

df = pd.read_excel(INPUT_FILE)

if df.empty:
    raise Exception("❌ No article data found")

offers = []

for _, row in df.iterrows():

    airline = str(row["Airlines Name"]).strip()
    iata = str(row["IATA"]).strip()
    validity = str(row["Validity"])

    cabin_map = {
        "First": row["First"],
        "Business": row["Bus"],
        "Premium Economy": row["Prem. eco"],
        "Economy": row["Eco"]
    }

    for cabin, deal in cabin_map.items():

        if pd.notna(deal) and deal != 0:

            offers.append({
                "airline": airline,
                "iata": iata,
                "cabin_class": cabin,
                "deal_percent": int(deal),
                "valid_till": validity,
                "source": "Zendesk Deal Sheet",
                "extracted_on": datetime.now().date().isoformat()
            })

out_df = pd.DataFrame(offers)

out_df.to_excel(OUTPUT_FILE, index=False)

print(f"✅ Extracted {len(out_df)} offers")
print("🏁 Offer extraction finished")
