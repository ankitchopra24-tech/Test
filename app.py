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
    st.error("❌ Offer file not found. Please ensure 'sample_offers.xlsx' is in your repo.")
    st.stop()

# Normalize column names
df.columns = df.columns.str.strip().str.lower()

# Dynamic mapping to handle any future renames
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

# ---- SEARCH FUNCTION ----
def find_best_offer(query, df, col_map):
    query = query.lower().strip()
    results = df.copy()

    # --- 1️⃣ Detect airline by name or IATA ---
    matched_airlines = []
    for _, row in df.iterrows():
        airline_name = str(row.get(col_map["airline"], "")).lower()
        airline_code = str(row.get(col_map["iata"], "")).lower()
        if airline_name in query or airline_code in query:
            matched_airlines.append((airline_name, airline_code))

    if matched_airlines:
        names = [a[0] for a in matched_airlines]
        codes = [a[1] for a in matched_airlines]
        results = df[
            df[col_map["airline"]].str.lower().isin(names) |
            df[col_map["iata"]].str.lower().isin(codes)
        ]

    # --- 2️⃣ Cabin class detection ---
    if "business" in query:
        results = results[results[col_map["cabin_class"]].str.contains("business", case=False, na=False)]
    elif "economy" in query:
        results = results[results[col_map["cabin_class"]].str.contains("economy", case=False, na=False)]

    # --- 3️⃣ Sector / route detection ---
    if any(loc in query for loc in ["dubai", "uae", "middle east"]):
        results = results[results[col_map["sector"]].str.contains("india", case=False, na=False)]
    elif any(loc in query for loc in ["europe", "france", "paris"]):
        results = results[results[col_map["sector"]].str.contains("international", case=False, na=False)]

    # --- 4️⃣ Sort by best deal ---
    if col_map["deal"] in results.columns:
        results = results.sort_values(by=col_map["deal"], ascending=False)

    # --- 5️⃣ Fallback fuzzy logic ---
    if results.empty:
        best_match = None
        best_score = 0.0
        for _, row in df.iterrows():
            text = f"{row.get(col_map['airline'], '')} {row.get(col_map['iata'], '')} {row.get(col_map['cabin_class'], '')}".lower()
            score = difflib.SequenceMatcher(None, query, text).ratio()
            if score > best_score:
                best_score = score
                best_match = row
        if best_match is not None and best_score > 0.3:
            return [best_match.to_dict()]
        else:
            return []

    # Return top 3 deals
    return results.head(3).to_dict(orient="records")

# ---- CHAT INPUT ----
query = st.text_input("💬 Type your question (e.g., 'Best deal on EK Business Class to Dubai')")

# ---- EXECUTE SEARCH ----
if query:
    st.write("🔍 Searching offers...")
    results = find_best_offer(query, df, col_map)

    if results:
        for row in results:
            st.markdown(f"""
            ✈️ **{row.get(col_map['airline'], 'Unknown')} ({row.get(col_map['iata'], 'N/A')})**
            - **Cabin:** {row.get(col_map['cabin_class'], 'N/A')}
            - **Deal:** {row.get(col_map['deal'], 'N/A')}%
            - **Fare Basis:** {row.get(col_map['fare_basis'], 'N/A')}
            - **Sector:** {row.get(col_map['sector'], 'N/A')}
            - **Valid Till:** {row.get(col_map['valid_till'], 'N/A')}
            - **Priority:** {row.get(col_map['priority'], 'N/A')}
            - **Conditions:** {row.get(col_map['conditions'], 'N/A')}
            ---
            """)
    else:
        st.warning("No matching offers found. Try another airline, class, or route!")

# ---- FOOTER ----
st.markdown("---")
st.caption("🤖 Built by Video AI • Smart Offer Finder Bot v4.0")
