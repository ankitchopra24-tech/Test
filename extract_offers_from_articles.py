import pandas as pd
from datetime import datetime

print("🚀 Offer extraction started...")

INPUT_FILE = "zendesk_articles_raw.xlsx"
OUTPUT_FILE = "offers_from_zendesk_articles.xlsx"

# =====================================================
# LOAD DATA
# =====================================================
df = pd.read_excel(INPUT_FILE)

if df.empty:
    raise Exception("❌ No article data found")

# Clean column names
df.columns = df.columns.str.strip().str.lower()

print("📊 Columns detected:", df.columns.tolist())

offers = []

# =====================================================
# EXTRACT OFFERS FROM STRUCTURED DEAL SHEET
# =====================================================
for _, row in df.iterrows():

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

        if pd.notna(deal) and str(deal).strip() != "" and float(deal) > 0:

            offers.append({
                "airline": airline,
                "iata": iata,
                "cabin_class": cabin,
                "deal_percent": int(float(deal)),
                "valid_till": validity,
                "source": "Zendesk Deal Sheet",
                "extracted_on": datetime.now().date().isoformat()
            })

# =====================================================
# SAVE OUTPUT
# =====================================================
out_df = pd.DataFrame(offers)

if out_df.empty:
    raise Exception("❌ No offers detected")

# Remove duplicates
out_df = out_df.drop_duplicates()

out_df.to_excel(OUTPUT_FILE, index=False)

print(f"✅ Extracted {len(out_df)} offers")
print(f"📄 Saved to {OUTPUT_FILE}")
print("🏁 Offer extraction finished")
