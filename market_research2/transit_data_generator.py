import pandas as pd

# Threshold: Within 1 arcminute of the edge boundary line
BORDER_THRESHOLD_DEG = 1.0 / 60.0  

def run_boundary_filter(csv_path="raw_market_session_ledger.csv"):
    df_ledger = pd.read_csv(csv_path)
    boundary_events = []
    
    # Absolute planetary grid including fast items & nodes. Ascendant excluded to stop noise.
    planetary_grid = ["Sun", "Moon", "Mars", "Mercury", "Venus", "Jupiter", "Saturn", "Rahu", "Ketu"]
    
    for idx, row in df_ledger.iterrows():
        time_str = row["Time"]
        
        for m in planetary_grid:
            d1_deg = row[f"M_{m}_D1_Deg"]
            nak_deg = row[f"M_{m}_Nak_Deg"]
            nak_span = 360.0 / 27.0  # 13.3333 degrees per Nakshatra
            
            # 1. --- D1 SIGN CUSP CROSSING CHECK ---
            if d1_deg <= BORDER_THRESHOLD_DEG or (30.0 - d1_deg) <= BORDER_THRESHOLD_DEG:
                edge_val = d1_deg if d1_deg <= BORDER_THRESHOLD_DEG else (30.0 - d1_deg)
                boundary_events.append({
                    "Time": time_str, 
                    "Layer": "D1 Sign Edge", 
                    "Planet": m, 
                    "Event": "Rashi Cusp Transition", 
                    "Dist_To_Edge": round(edge_val, 5)
                })
                
            # 2. --- NAKSHATRA / D9 SIGN CUSP CHECK ---
            if nak_deg <= BORDER_THRESHOLD_DEG or (nak_span - nak_deg) <= BORDER_THRESHOLD_DEG:
                edge_val = nak_deg if nak_deg <= BORDER_THRESHOLD_DEG else (nak_span - nak_deg)
                boundary_events.append({
                    "Time": time_str, 
                    "Layer": "Nakshatra / D9 Edge", 
                    "Planet": m, 
                    "Event": "Constellation Border Crossover", 
                    "Dist_To_Edge": round(edge_val, 5)
                })
                
    return pd.DataFrame(boundary_events).drop_duplicates(subset=["Time", "Planet", "Event"])

if __name__ == "__main__":
    try:
        df_borders = run_boundary_filter()
        print("\n--- DETECTED PLANETARY BOUNDARY TRANSITIONS (D1 & NAKSHATRA/D9) ---")
        print(df_borders.to_string(index=False))
    except FileNotFoundError:
        print("Error: Run transit_data_generator.py first to create the base ledger.")
