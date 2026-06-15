import pandas as pd
import numpy as np

def run_method_a_filter(csv_path="raw_market_session_ledger.csv"):
    df_ledger = pd.read_csv(csv_path)
    records = []
    
    all_bodies = ["Ascendant", "Sun", "Moon", "Mars", "Mercury", "Venus", "Jupiter", "Saturn", "Rahu", "Ketu"]
    
    for idx, row in df_ledger.iterrows():
        time_str = row["Time"]
        
        for m in all_bodies:
            for b in all_bodies:
                
                # --- D1 LAYER: TRUNCATED INTEGER MATCH ---
                m_d1_sign = int(row[f"M_{m}_D1_Sign"])
                b_d1_sign = int(row[f"B_{b}_D1_Sign"])
                
                # Truncate degrees to pure integers (e.g., 27.4532 -> 27)
                m_d1_deg_int = int(np.floor(row[f"M_{m}_D1_Deg"]))
                b_d1_deg_int = int(np.floor(row[f"B_{b}_D1_Deg"]))
                
                if m_d1_sign == b_d1_sign and m_d1_deg_int == b_d1_deg_int:
                    tag = "COLOR_RED_OBSERVE" if m == "Ascendant" else "ACTIONABLE_TREND_NODE"
                    records.append({
                        "Time": time_str,
                        "System": "Method A (Whole Degree)",
                        "Layer": "D1 Macro",
                        "Market_Body": f"Market {m}",
                        "Birth_Body": f"Birth {b}",
                        "Matched_Sign": m_d1_sign,
                        "Matched_Integer_Deg": m_d1_deg_int,
                        "Status": tag
                    })
                
                # --- D9 LAYER: TRUNCATED INTEGER MATCH ---
                m_d9_sign = int(row[f"M_{m}_D9_Sign"])
                b_d9_sign = int(row[f"B_{b}_D9_Sign"])
                
                m_d9_deg_int = int(np.floor(row[f"M_{m}_D9_Deg"]))
                b_d9_deg_int = int(np.floor(row[f"B_{b}_D9_Deg"]))
                
                if m_d9_sign == b_d9_sign and m_d9_deg_int == b_d9_deg_int:
                    tag = "COLOR_RED_OBSERVE" if m == "Ascendant" else "ACTIONABLE_TREND_NODE"
                    records.append({
                        "Time": time_str,
                        "System": "Method A (Whole Degree)",
                        "Layer": "D9 Micro",
                        "Market_Body": f"Market {m}",
                        "Birth_Body": f"Birth {b}",
                        "Matched_Sign": m_d9_sign,
                        "Matched_Integer_Deg": m_d9_deg_int,
                        "Status": tag
                    })
                    
    df_out = pd.DataFrame(records)
    return df_out.drop_duplicates(subset=["Time", "Layer", "Market_Body", "Birth_Body"])

if __name__ == "__main__":
    try:
        df_a = run_method_a_filter()
        print("\n--- METHOD A: WHOLE-DEGREE INTEGER MATCHES ---")
        print(df_a.to_string(index=False))
    except FileNotFoundError:
        print("Error: Run transit_data_generator.py first.")
