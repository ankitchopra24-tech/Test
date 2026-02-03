import pandas as pd
import re
from datetime import datetime

# -------------------------------------------------
# LOAD RAW ZENDESK ARTICLES
# -------------------------------------------------
df = pd.read_excel("zendesk_articles_raw.xlsx")

offers = []

# Airline reference map (extend later)
AIRLINES = {
    "emirates": "EK",
    "air france": "AF",
    "klm": "KL",
    "delta": "DL",
    "air india": "AI",
    "lufthansa": "LH",
    "british airways": "BA",
    "qatar": "QR",
    "singapore airlines": "SQ"
}

# -------------------------------------------------
# EXTRACT OFFER DATA
# -------------------------------------------------
for _, row in df.iterrows():
    text = str(row["content"]).lower()

    for airline, iata in AIRLINES.items():
        if airline in text:
            # Deal %
            deal_match = re.search(r"(\d+(\.\d+)?)\s*%", text)
            deal = float(deal_match.group(1)) if deal_match else None

            # Cabin class
            cabin = "Business" if "business" in text else "Economy" if "economy" in text else "All"

            # Validity date
            date_match = re.search(r"(\d{1,2}\s\w+\s\d{4})", text)
            valid_till = None
            if date_match:
                try:
                    valid_till = datetime.strptime(date_match.group(1), "%d %b %Y")
                except:
                    pass

            offers.append({
                "airline": airline.title(),
                "iata": iata,
                "cabin_class": cabin,
                "deal_percent": deal,
                "valid_till": valid_till,
                "source_article": row["title"],
                "source": "Zendesk KB"
            })

# -------------------------------------------------
# SAVE STRUCTURED OFFERS
# -------------------------------------------------
offers_df = pd.DataFrame(offers)
offers_df.to_excel("offers_from_zendesk_articles.xlsx", index=False)

print(f"✅ Extracted {len(offers_df)} offers from Zendesk articles")
