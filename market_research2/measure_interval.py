import pandas as pd
import numpy as np

# Velocity-to-interval limits mapping (True Astronomical Hierarchy)
INTERVAL_LIMITS = {
    "Moon": 0.12,         # Sprinter: tight corridor to isolate rapid turning points
    "Mercury": 0.25,      # Tactical stalemate-breaker
    "Venus": 0.30,        # Tactical stalemate-breaker
    "Sun": 0.50,
    "Mars": 0.50,
    "Jupiter": 0.75,      # Macro environmental gear
    "Saturn": 0.75,      # Macro environmental gear
    "Rahu": 1.00,         # Heavy structural node
    "Ketu": 1.00,         # Heavy structural node
    "Ascendant": 0.05    # Local horizon intersection baseline
}

def calculate_coincidence_index(transit_long, birth_long, max_interval):
    """Calculates the alignment proximity. 100% means exact spatial conjunction."""
    delta = abs(transit_long - birth_long)
    if delta > 180.0:
        delta = 360.0 - delta
    if delta >= max_interval:
        return 0.0
    return round((1.0 - (delta / max_interval)) * 100.0, 2)

def reverse_engineer_moment(target_time, csv_path="raw_market_session_ledger.csv"):
    df_ledger = pd.read_csv(csv_path)
    
    # Isolate the exact minute row of your historical market event
    moment_row = df_ledger[df_ledger["Time"] == target_time]
    
    if moment_row.empty:
        print(f"Error: Timestamp '{target_time}' not found in the baseline ledger.")
        return
    
    row = moment_row.iloc[0]
    snapshot_records = []
    
    transit_bodies = ["Sun", "Moon", "Mars", "Mercury", "Venus", "Jupiter", "Saturn", "Rahu", "Ketu"]
    birth_targets  = ["Ascendant", "Sun", "Moon", "Mars", "Mercury", "Venus", "Jupiter", "Saturn", "Rahu", "Ketu"]
    
    for m in transit_bodies:
        m_total = row[f"M_{m}_Total"]
        max_i = INTERVAL_LIMITS[m]
        
        for b in birth_targets:
            b_total = row[f"B_{b}_Total"]
            
            # --- D1 MACRO REVERSE INSPECTION ---
            d1_score = calculate_coincidence_index(m_total, b_total, max_i)
            if d1_score > 0.0:
                snapshot_records.append({
                    "Layer": "D1 Macro",
                    "Transiting_Planet": m,
                    "Birth_Target": b,
                    "Coincidence_Index": f"{d1_score}%",
                    "Proximity_Status": "CRITICAL_TRIGGER" if d1_score >= 85.0 else "PRESSURE_ZONE"
                })
            
            # --- D9 MICRO REVERSE INSPECTION ---
            m_d9_sign = int(row[f"M_{m}_D9_Sign"])
            b_d9_sign = int(row[f"B_{b}_D9_Sign"])
            
            if m_d9_sign == b_d9_sign:
                d9_score = calculate_coincidence_index(row[f"M_{m}_D9_Deg"], row[f"B_{b}_D9_Deg"], max_i)
                if d9_score > 0.0:
                    snapshot_records.append({
                        "Layer": "D9 Micro",
                        "Transiting_Planet": m,
                        "Birth_Target": b,
                        "Coincidence_Index": f"{d9_score}%",
                        "Proximity_Status": "CRITICAL_TRIGGER" if d9_score >= 85.0 else "PRESSURE_ZONE"
                    })
                    
    df_snapshot = pd.DataFrame(snapshot_records)
    print(f"\n==================================================================")
    print(f" REVERSE ENGINEERING REVERSAL TIME: {target_time}")
    print(f"==================================================================")
    if df_snapshot.empty:
        print("No structural intervals or birth targets breached at this minute.")
    else:
        print(df_snapshot.to_string(index=False))

if __name__ == "__main__":
    # Change this string to match the exact minute of the market event you want to audit
    TARGET_MARKET_MOMENT = "10:30:00"
    
    try:
        reverse_engineer_moment(TARGET_MARKET_MOMENT)
    except FileNotFoundError:
        print("Error: Missing base ledger. Run transit_data_generator.py first.")
