def find_best_offer(query, df, col_map):
    query = query.lower().strip()
    results = df.copy()

    # --- 1️⃣ Airline detection (by name or IATA code) ---
    matched_airlines = []
    for _, row in df.iterrows():
        airline_name = str(row[col_map["airline"]]).lower()
        airline_code = str(row[col_map["iata"]]).lower()
        if airline_name in query or airline_code in query:
            matched_airlines.append((airline_name, airline_code))

    if matched_airlines:
        matched_names = [a[0] for a in matched_airlines]
        matched_codes = [a[1] for a in matched_airlines]
        results = df[
            df[col_map["airline"]].str.lower().isin(matched_names) |
            df[col_map["iata"]].str.lower().isin(matched_codes)
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

    # --- 4️⃣ Rank by best deal (if applicable) ---
    if col_map["deal"] in results.columns:
        results = results.sort_values(by=col_map["deal"], ascending=False)

    # --- 5️⃣ Fallback fuzzy logic if no airline found ---
    if results.empty:
        import difflib
        best_match = None
        best_score = 0.0
        for _, row in df.iterrows():
            text = f"{row[col_map['airline']]} {row[col_map['iata']]} {row[col_map['cabin_class']]}".lower()
            score = difflib.SequenceMatcher(None, query, text).ratio()
            if score > best_score:
                best_score = score
                best_match = row
        if best_match is not None and best_score > 0.3:
            return [best_match.to_dict()]
        else:
            return []

    # --- Return top results ---
    return results.head(3).to_dict(orient="records")
