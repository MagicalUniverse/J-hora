def filter_exact_alignments(df_ledger, orbis=0.05):
    alignments = []
    # Fully expanded to include Mercury, Venus, Rahu, and Ketu
    all_bodies = ["Ascendant", "Sun", "Moon", "Mars", "Mercury", "Venus", "Jupiter", "Saturn", "Rahu", "Ketu"]
    
    for idx, row in df_ledger.iterrows():
        for m in all_bodies:
            for b in all_bodies:
                m_total = row[f"M_{m}_Total"]
                b_total = row[f"B_{b}_Total"]
                
                if abs(m_total - b_total) <= orbis:
                    tag = "COLOR_RED_OBSERVE" if m == "Ascendant" else "ACTIONABLE_TREND_NODE"
                    alignments.append({
                        "Time": row["Time"], 
                        "Type": "D1 Conjoint",
                        "Market_Body": m, 
                        "Birth_Body": b,
                        "Exact_Delta": round(m_total - b_total, 5), 
                        "Status": tag
                    })
    return pd.DataFrame(alignments)
