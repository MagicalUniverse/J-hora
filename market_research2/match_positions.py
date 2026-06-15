import pandas as pd

# Define threshold: 0.05 degrees (~3 arcminutes)
PROXIMITY_ORBIT_DEG = 0.05

def run_alignment_filter(csv_path="raw_market_session_ledger.csv"):
    df_ledger = pd.read_csv(csv_path)
    alignments = []
    
    # Complete planetary roster + fast-moving execution trigger (Ascendant)
    all_bodies = ["Ascendant", "Sun", "Moon", "Mars", "Mercury", "Venus", "Jupiter", "Saturn", "Rahu", "Ketu"]
    
    for idx, row in df_ledger.iterrows():
        time_str = row["Time"]
        
        for m in all_bodies:
            for b in all_bodies:
                
                # 1. --- D1 MACRO LONGITUDE CHECK ---
                m_total = row[f"M_{m}_Total"]
                b_total = row[f"B_{b}_Total"]
                
                if abs(m_total - b_total) <= PROXIMITY_ORBIT_DEG:
                    status = "COLOR_RED_OBSERVE" if m == "Ascendant" else "ACTIONABLE_TREND_NODE"
                    alignments.append({
                        "Time": time_str, 
                        "Layer": "D1 Macro",
                        "Market_Body": f"Market {m}", 
                        "Birth_Body": f"Birth {b}",
                        "Exact_Delta": round(m_total - b_total, 5), 
                        "Status": status
                    })
                
                # 2. --- D9 MICRO NAVAMSA CHECK ---
                m_d9_sign = row[f"M_{m}_D9_Sign"]
                m_d9_deg  = row[f"M_{m}_D9_Deg"]
                b_d9_sign = row[f"B_{b}_D9_Sign"]
                b_d9_deg  = row[f"B_{b}_D9_Deg"]
                
                # Planets must land in the same divisional sign block AND match degrees
                if m_d9_sign == b_d9_sign and abs(m_d9_deg - b_d9_deg) <= PROXIMITY_ORBIT_DEG:
                    status = "COLOR_RED_OBSERVE" if m == "Ascendant" else "ACTIONABLE_TREND_NODE"
                    alignments.append({
                        "Time": time_str, 
                        "Layer": "D9 Micro",
                        "Market_Body": f"Market {m}", 
                        "Birth_Body": f"Birth {b}",
                        "Exact_Delta": round(m_d9_deg - b_d9_deg, 5), 
                        "Status": status
                    })
                    
    df_out = pd.DataFrame(alignments)
    return df_out.drop_duplicates(subset=["Time", "Layer", "Market_Body", "Birth_Body"])

if __name__ == "__main__":
    try:
        df_alignments = run_alignment_filter()
        print("\n--- DETECTED INTER-CHART ALIGNMENTS (D1 & D9) ---")
        print(df_alignments.to_string(index=False))
    except FileNotFoundError:
        print("Error: Run transit_data_generator.py first to create the base ledger.")
