import streamlit as st
import pandas as pd
import difflib

# ---- PAGE SETUP ----
st.set_page_config(page_title="Offer Finder Bot", page_icon="✈️")
st.title("✈️ Airline Offer Finder Bot")
st.markdown("Ask me about the best airline deals from your updated offer sheet!")

# ---- LOAD DATA ----
df = pd.read_excel("sample_offers (3).xlsx")
df.columns = df.columns.str.strip().str.lower()

# ---- QUERY INPUT ----
query = st.text_input("💬 Type your question (e.g., 'Best deal on Emirates Business Class')")

# ---- SEARCH LOGIC ----
def find_best_offer(query, df):
    query = query.lower().strip()
    best_match = None
    best_score = 0.0

    # Dynamic matching columns
    airline_col = "airline"
    iata_col = "iata"
    class_col = "cabin_class"

    for _, row in df.iterrows():
        text = f"{row[airline_col]} {row[iata_col]} {row[class_col]}".lower()
        score = difflib.SequenceMatcher(None, query, text).ratio()
        if score > best_score:
            best_score = score
            best_match = row

    # Additional route / keyword filter examples
    if "dubai" in query or "uae" in query:
        df = df[df["sector"].str.contains("india", case=False, na=False)]
        if not df.empty:
            return df.to_dict(orient="records")

    if best_match is not None and best_score > 0.3:
        return [best_match.to_dict()]
    else:
        return []

# ---- DISPLAY RESULTS ----
if query:
    st.write("🔍 Searching offers...")
    results = find_best_offer(query, df)

    if results:
        for row in results:
            st.markdown(f"""
            ✈️ **{row.get('airline', 'Unknown')} ({row.get('iata', 'N/A')})**
            - **Cabin:** {row.get('cabin_class', 'N/A')}
            - **Deal:** {row.get('deal_%', 'N/A')}%
            - **Fare Basis:** {row.get('fare_basis', 'N/A')}
            - **Travel Type:** {row.get('travel_type', 'N/A')}
            - **Sector:** {row.get('sector', 'N/A')}
            - **Valid Till:** {row.get('valid_till', 'N/A')}
            - **Priority:** {row.get('priority', 'N/A')}
            - **Conditions:** {row.get('key_conditions', 'N/A')}
            ---
            """)
    else:
        st.warning("No matching offers found. Try another airline, class, or route name!")

st.markdown("---")
st.caption("🤖 Built by Video AI • Smart Offer Finder v3.0")
