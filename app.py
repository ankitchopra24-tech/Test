import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Offer Finder Bot", page_icon="✈️")
st.title("✈️ Airline Offer Finder Bot")
st.markdown("Ask me about the best airline deals from your offer sheet!")

# Load data from Excel
df = pd.read_excel("sample_offers.xlsx")

query = st.text_input("💬 Type your question (e.g., 'Best offer on Emirates Business Class')")

if query:
    st.write("🔍 Searching offers...")
   import difflib

def find_best_offer(query, df):
    query = query.lower()

    # Prioritize airline name or IATA code
    best_match = None
    best_score = 0

    for _, row in df.iterrows():
        text = f"{row['Airline']} {row['IATA']} {row['Class']}".lower()
        score = difflib.SequenceMatcher(None, query, text).ratio()

        if score > best_score:
            best_score = score
            best_match = row

    # Threshold to avoid false matches
    if best_match is not None and best_score > 0.3:
        return [best_match]
    else:
        return []

results = find_best_offer(query, df)


    if not results.empty:
        for _, row in results.iterrows():
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
        st.warning("No matching offers found. Try another airline or class name!")

st.markdown("---")
st.caption("🤖 Built by Video AI using Streamlit • Demo Chatbot v1.0")
