import pandas as pd

# Permanent natural rulership blueprint (1-indexed signs: 1=Aries ... 12=Pisces)
SIGN_LORDS = {
    1: "Mars",    2: "Venus",   3: "Mercury", 4: "Moon",    5: "Sun",     6: "Mercury",
    7: "Venus",   8: "Mars",    9: "Jupiter", 10: "Saturn", 11: "Saturn", 12: "Jupiter"
}

def evaluate_geometric_drishti(t_name, t_sign, b_sign):
    """Computes exact sign-to-sign aspect distance (1-indexed counting)."""
    distance = (b_sign - t_sign) % 12 + 1
    
    # Core Geometric Glance Rules
    if t_name == "Jupiter" and distance in [5, 7, 9]: return f"asp-{distance}H"
    if t_name == "Mars" and distance in [4, 7, 8]: return f"asp-{distance}H"
    if t_name == "Saturn" and distance in [3, 7, 10]: return f"asp-{distance}H"
    if t_name in ["Sun", "Moon", "Venus", "Mercury"] and distance == 7: return "asp-7H"
    if t_name in ["Rahu", "Ketu"] and distance in [5, 9]: return f"asp-{distance}H"
    return None

def calculate_functional_nature(market_asc_sign):
    """
    Derives temporary house placements relative to the active Market Ascendant.
    Identifies active Bullish and Bearish planetary actors for the current minute.
    """
    # Map out the active sky: house 1 starts at the current market ascendant sign
    house_to_sign_map = {h: (market_asc_sign + h - 2) % 12 + 1 for h in range(1, 13)}
    
    # Bullish Drivers: 5th (Speculation), 9th (Fortune), 11th (Net Gains) House Lords
    bull_lords = [SIGN_LORDS[house_to_sign_map[h]] for h in [5, 9, 11]]
    
    # Bearish Drivers: 6th (Obstacles), 8th (Vulnerability), 12th (Losses) House Lords
    bear_lords = [SIGN_LORDS[house_to_sign_map[h]] for h in [6, 8, 12]]
    
    return set(bull_lords), set(bear_lords)

def execute_unified_aspect_analysis(csv_path="raw_market_session_ledger.csv"):
    df_ledger = pd.read_csv(csv_path)
    unified_records = []
    
    # Planetary inputs (Market Ascendant cannot cast an aspect, it only receives them)
    transit_planets = ["Sun", "Moon", "Mars", "Mercury", "Venus", "Jupiter", "Saturn", "Rahu", "Ketu"]
    birth_targets  = ["Ascendant", "Sun", "Moon", "Mars", "Mercury", "Venus", "Jupiter", "Saturn", "Rahu", "Ketu"]
    
    for idx, row in df_ledger.iterrows():
        time_str = row["Time"]
        m_asc_sign = int(row["M_Ascendant_D1_Sign"])
        
        # 1. Update the functional framework for this exact minute
        bull_agents, bear_agents = calculate_functional_nature(m_asc_sign)
        
        for t_name in transit_planets:
            t_sign = int(row[f"M_{t_name}_D1_Sign"])
            
            for b_name in birth_targets:
                b_sign = int(row[f"B_{b_name}_D1_Sign"])
                
                # 2. Check for an active geometric connection
                aspect_tag = evaluate_geometric_drishti(t_name, t_sign, b_sign)
                
                if aspect_tag:
                    # 3. Intersect geometry with functional status
                    if t_name in bull_agents:
                        signal = "BULL"
                    elif t_name in bear_agents:
                        signal = "BEAR"
                    else:
                        signal = "NEUTRAL"
                        
                    unified_records.append({
                        "Time": time_str,
                        "Transit_Planet": t_name,
                        "Aspect": aspect_tag,
                        "Birth_Target": b_name,
                        "Signal": signal
                    })
                    
    df_output = pd.DataFrame(unified_records)
    # Deduplicate matching events inside the same minute interval
    return df_output.drop_duplicates(subset=["Time", "Transit_Planet", "Birth_Target"])

if __name__ == "__main__":
    try:
        df_results = execute_unified_aspect_analysis()
        print("\n--- UNIFIED GEOMETRIC ASPECTS & FUNCTIONAL SENTIMENT ---")
        print(df_results.head(20).to_string(index=False))
    except FileNotFoundError:
        print("Error: Missing 'raw_market_session_ledger.csv'. Run transit_data_generator.py first.")
