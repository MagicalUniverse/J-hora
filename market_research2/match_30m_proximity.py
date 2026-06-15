import pandas as pd

# 30 minutes of arc mapping directly to a 0.5 decimal degree spatial tolerance corridor
PRECISION_ORBIT_DEG = 0.5000

def run_method_b_filter(csv_path="raw_market_session_ledger.csv"):
    df_ledger = pd.read_csv(csv_path)
    records = []
    
    all_bodies = ["Ascendant", "Sun", "Moon", "Mars", "Mercury", "Venus", "Jupiter", "Saturn", "Rahu", "Ketu"]
    
    for idx, row in df_ledger.iterrows():
        time_str = row["Time"]
        
        for m in all_bodies:
            for b in all_bodies:
                
                # --- D1 LAYER: PRECISION ORBIT CORRIDOR ---
                m_total = row[f"M_{m}_Total"]
                b_total = row[f"B_{b}_Total"]
                
                if abs(m_total - b_total) <= PRECISION_ORBIT_DEG:
                    tag = "COLOR_RED_OBSERVE" if m == "Ascendant" else "ACTIONABLE_TREND_NODE"
                    records.append({
                        "Time": time_str,
                        "System": "Method B (Proximity Corridor)",
                        "Layer": "D1 Macro",
                        "Market_Body": f"Market {m}",
                        "Birth_Body": f"Birth {b}",
                        "Exact_Delta": round(m_total - b_total, 5),
                        "Status": tag
                    })
                
                # --- D9 LAYER: PRECISION ORBIT CORRIDOR ---
                m_d9_sign = row[f"M_{m}_D9_Sign"]
                m_d9_deg  = row[f"M_{m}_D9_Deg"]
                b_d9_sign = row[f"B_{b}_D9_Sign"]
                b_d9_deg  = row[f"B_{b}_D9_Deg"]
                
                if m_d9_sign == b_d9_sign and abs(m_d9_deg - b_d9_deg) <= PRECISION_ORBIT_DEG:
                    tag = "COLOR_RED_OBSERVE" if m == "Ascendant" else "ACTIONABLE_TREND_NODE"
                    records.append({
                        "Time": time_str,
                        "System": "Method B (Proximity Corridor)",
                        "Layer": "D9 Micro",
                        "Market_Body": f"Market {m}",
                        "Birth_Body": f"Birth {b}",
                        "Exact_Delta": round(m_d9_deg - b_d9_deg, 5),
                        "Status": tag
                    })
                    
    df_out = pd.DataFrame(records)
    return df_out.drop_duplicates(subset=["Time", "Layer", "Market_Body", "Birth_Body"])

if __name__ == "__main__":
    try:
        df_b = run_method_b_filter()
        print("\n--- METHOD B: ABSOLUTE PROXIMITY CORRIDOR MATCHES ---")
        print(df_b.to_string(index=False))
    except FileNotFoundError:
        print("Error: Run transit_data_generator.py first.")
