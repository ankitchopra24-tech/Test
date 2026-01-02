import streamlit as st
import pandas as pd
import difflib

# ---- PAGE SETUP ----
st.set_page_config(page_title="Offer Finder Bot", page_icon="✈️")
st.title("✈️ Airline Offer Finder Bot")
st.markdown("Ask me about the best airline deals from your updated offer sheet!")

# ---- LOAD DATA ----
df = pd.read_excel("sample_offers.xlsx")
df.columns = df.columns.str.strip().str.lower()

# Handle special character column names safely
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

# ---- QUERY INPUT ----
query = st.text_input("💬 Type your question (e.g., 'Best deal on Emirates Business Class')")

# ---- SEARCH LOGIC ----
def find_best_offer(query, df, col_map):
    query = query.lower().strip()
    best_match = None
    best_score = 0.0

    for _, row in df.iterrows():
        text_parts = [
            str(row.get(col_map["airline"], "")),
            str(row.get(col_map["iata"], "")),
            str(row.get(col_map["cabin_class"], "")),
        ]
        text = " ".join(text_parts).lower()
        score = difflib.SequenceMatcher(None, query, text).ratio()
        if score > best_score:
            best_score = score
            best_match = row

    # Route / sector detection
    if any(keyword in query for keyword in ["dubai", "uae", "middle east"]):
        filtered = df[df[col_map["sector"]].str.contains("india", case=False, na=False)]
        if not filtered.empty:
            return filtered.to_dict(orient="records")

    if best_match is not None and best_score > 0.3:
        return [best_match.to_dict()]
    return []

# ---- DISPLAY RESULTS ----
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

st.markdown("---")
st.caption("🤖 Built by Video AI • Smart Offer Finder v3.2")
