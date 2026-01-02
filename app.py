import streamlit as st
import pandas as pd
import re
import difflib  # make sure this is at the top with other imports

# ---- PAGE SETUP ----
st.set_page_config(page_title="Offer Finder Bot", page_icon="✈️")
st.title("✈️ Airline Offer Finder Bot")
st.markdown("Ask me about the best airline deals from your offer sheet!")

# ---- LOAD DATA ----
df = pd.read_excel("sample_offers.xlsx")

# ---- QUERY INPUT ----
query = st.text_input("💬 Type your question (e.g., 'Best offer on Emirates Business Class')")

# ---- SEARCH LOGIC ----
def find_best_offer(query, df):
    query = query.lower().strip()
    best_match = None
    best_score = 0.0

    # Fuzzy match: find the airline most relevant to the user’s query
    for _, row in df.iterrows():
        text = f"{row['Airline']} {row['IATA']} {row['Class']}".lower()
        score = difflib.SequenceMatcher(None, query, text).ratio()
        if score > best_score:
            best_score = score
            best_match = row

    # Route / keyword handling
    if "thai" in query or "bangkok" in query or "delhi" in query:
        df = df[df["Airline"].str.contains("Thai", case=False, na=False) | 
                df["IATA"].str.contains("TG", case=False, na=False)]
        if not df.empty:
            return df.to_dict(orient="records")

    # If fuzzy match confidence is decent, return it
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
            ✈️ **{row['Airline']} ({row['IATA']})**
            - **Class:** {row['Class']}
            - **Offer:** {row['Offer']}
            - **Validity:** {row['Validity']}
            - **Exclusions:** {row['Exclusions']}
            - **Notes:** {row['Notes']}
            ---
            """)
    else:
        st.warning("No matching offers found. Try another airline or route name!")

st.markdown("---")
st.caption("🤖 Built by Video AI • Enhanced Offer Finder Bot v2.0")
