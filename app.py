def find_best_offer(query, df, col_map):
    query = query.lower().strip()
    results = df.copy()

    # --- 1️⃣ Airline detection ---
    airline_hits = []
    for airline in df[col_map["airline"]].unique():
        if airline.lower() in query:
            airline_hits.append(airline.lower())
    for code in df[col_map["iata"]].unique():
        if code.lower() in query:
            airline_hits.append(code.lower())

    if airline_hits:
        results = results[results[col_map["airline"]].str.lower().isin(airline_hits) |
                          results[col_map["iata"]].str.lower().isin(airline_hits)]

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

    # --- 4️⃣ Rank by best deal ---
    if col_map["deal"] in results.columns:
        results = results.sort_values(by=col_map["deal"], ascending=False)

    # --- 5️⃣ Fallback if nothing matched ---
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

    # Return top 3 matches for clarity
    return results.head(3).to_dict(orient="records")
