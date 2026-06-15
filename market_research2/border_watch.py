def filter_cusp_transitions(df_ledger, threshold=1.0/60.0):
    cusp_events = []
    # Complete planetary line-up including nodes and fast inner planets
    planetary_grid = ["Sun", "Moon", "Mars", "Mercury", "Venus", "Jupiter", "Saturn", "Rahu", "Ketu"]
    
    for idx, row in df_ledger.iterrows():
        for m in planetary_grid:
            d1_deg = row[f"M_{m}_D1_Deg"]
            nak_deg = row[f"M_{m}_Nak_Deg"]
            
            if d1_deg <= threshold or (30.0 - d1_deg) <= threshold:
                cusp_events.append({
                    "Time": row["Time"], "Body": m, 
                    "Boundary": "Rashi Cusp Edge", "Exact_Deg": round(d1_deg, 4)
                })
            if nak_deg <= threshold or ((360.0/27.0) - nak_deg) <= threshold:
                cusp_events.append({
                    "Time": row["Time"], "Body": m, 
                    "Boundary": "Nakshatra Cusp Edge", "Exact_Deg": round(nak_deg, 4)
                })
                
    return pd.DataFrame(cusp_events)
