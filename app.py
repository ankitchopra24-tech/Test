import streamlit as st
import pandas as pd
import difflib

# ---- PAGE CONFIG ----
st.set_page_config(page_title="Airline Offer Finder Bot", page_icon="✈️")
st.title("✈️ Airline Offer Finder Bot")
st.markdown("Ask me about the best airline deals from your updated offer sheet!")

# ---- LOAD EXCEL DATA ----
try:
    df = pd.read_excel("sample_offers.xlsx")
except FileNotFoundError:
    st.error("❌ Offer file not found. Please ensure 'sample_offers.xlsx' is uploaded to your GitHub repo.")
    st.stop()

# Normalize column names
df.columns = df.columns.str.strip().str.lower()

# Dynamic column mapping
col_map = {
    "airline": next((c for c in df.columns if "airline" in c), None),
    "iata": next((c for c in df.columns if "iata" in c), None),
    "cabin_class": next((c for c in df.columns if "cabin" in c or "class" in c), None),
    "deal": next((c for c in df.columns if "deal" in c), None),
    "fare_basis": next((c for c in df.columns if "fare" in c), None),
    "sector": next((c for c in df.columns if "sector" in c), None),
    "valid_till": next((c for c in df.columns if "valid" in c), None),
    "priority": next((c for c in df.columns if "priority" in c), None),
    "conditions": next((c for c in df.columns if "condition" in c), None)
}

# ---- SMART SEARCH FUNCTION ----
def find_best_offer(query, df, col_map):
    query = query.lower().strip()
    results = df.copy()

    # --- 1️⃣ Exact Airline / IATA match ---
    for code in df[col_map["iata"]].dropna().unique():
        if f" {code.lower()} " in f" {query} " or query.startswith(code.lower()):
            results = df[df[col_map["iata"]].str.lower() == code.lower()]
            break
    for name in df[col_map["airline"]].dropna().unique():
        if name.lower() in query:
            results = df[df[col_map["airline"]].str.lower() == name.lower()]
            break

    # --- 2️⃣ Cabin / class detection ---
    if "business" in query:
        results = results[results[col_map["cabin_class"]].str.contains("business", case=False, na=False)]
    elif "economy" in query:
        results = results[results[col_map["cabin_class"]].str.contains("economy", case=False, na=False)]

    # --- 3️⃣ Location-aware route detection ---
    location_keywords = {
        "dubai": "middle east|dubai|uae|india",
        "uae": "middle east|dubai|uae",
        "india": "india|delhi|mumbai|chennai|bengaluru",
        "europe": "europe|france|paris|london|amsterdam|germany|spain",
        "usa": "usa|america|new york|atlanta|los angeles",
        "australia": "australia|sydney|melbourne",
        "asia": "asia|singapore|bangkok|tokyo|malaysia|hong kong",
        "africa": "africa|nairobi|johannesburg|cairo"
    }

    for city, pattern in location_keywords.items():
        if city in query:
            results = df[
                df[col_map["sector"]].str.contains(pattern, case=False, na=False) |
                df[col_map["conditions"]].str.contains(pattern, case=False, na=False)
            ]
            break

    # --- 4️⃣ Sort by highest deal value ---
    if not results.empty and col_map["deal"] in results.columns:
        results = results.sort_values(by=col_map["deal"], ascending=False)

    # --- 5️⃣ Fuzzy fallback (if no results) ---
    if results.empty:
        best_match = None
        best_score = 0.0
        for _, row in df.iterrows():
            text = f"{row.get(col_map['airline'], '')} {row.get(col_map['iata'], '')} {row.get(col_map['sector'], '')}".lower()
            score = difflib.SequenceMatcher(None, query, text).ratio()
            if score > best_score:
                best_score = score
                best_match = row
        if best_match is not None and best_score > 0.4:
            return [best_match.to_dict()]
        else:
            return []

    # --- 6️⃣ Limit to top 5 results ---
    return results.head(5).to_dict(orient="records")

# ---- USER INPUT ----
query = st.text_input("💬 Type your query (e.g., 'Best deal on EK Business Class to Dubai')")

# ---- SEARCH EXECUTION ----
if query:
    st.write("🔍 Searching offers...")
    results = find_best_offer(query, df, col_map)

    if results:
        for i, row in enumerate(results, start=1):
            # Format the offer details
            offer_text = f"""
✈️ {row.get(col_map['airline'], 'Unknown')} ({row.get(col_map['iata'], 'N/A')})
Cabin: {row.get(col_map['cabin_class'], 'N/A')}
Deal: {row.get(col_map['deal'], 'N/A')}%
Fare Basis: {row.get(col_map['fare_basis'], 'N/A')}
Sector: {row.get(col_map['sector'], 'N/A')}
Valid Till: {row.get(col_map['valid_till'], 'N/A')}
Priority: {row.get(col_map['priority'], 'N/A')}
Conditions: {row.get(col_map['conditions'], 'N/A')}
"""

            # Display result with a copy button
            st.markdown(f"### ✈️ Offer {i}")
            st.text(offer_text.strip())
            st.code(offer_text.strip(), language="markdown")
            st.button(f"📋 Copy Offer {i}", key=f"copy_{i}", help="Click to copy this offer text")

            st.markdown("---")

    else:
        st.warning("⚠️ No matching offers found. Try another airline, class, or route!")

# ---- FOOTER ----
st.markdown("---")
st.caption("🤖 Built by Video AI • Smart Offer Finder Bot v6.0 • With Copy Buttons ✈️")
