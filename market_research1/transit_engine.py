import datetime
import swisseph as swe
import pandas as pd

# =====================================================================
# 1. BASELINE CONSTRAINTS & CONSTANTS
# =====================================================================
DEFAULT_BIRTH_DATE = "1814.05.17"
DEFAULT_BIRTH_TIME = "12:27:12"
DEFAULT_BIRTH_TZ   = 0.0

DEFAULT_LAT = 60.3011
DEFAULT_LON = 11.1717
DEFAULT_ALT = 25.0

swe.set_sid_mode(swe.SIDM_LAHIRI)
PROXIMITY_ORBIT_DEG = 0.05  # Within ~3 arcminutes
BORDER_THRESHOLD_DEG = 1.0 / 60.0  # 1 arcminute sign/nakshatra cusp

SIGN_LORDS = {
    1: "Mars", 2: "Venus", 3: "Mercury", 4: "Moon", 5: "Sun", 6: "Mercury",
    7: "Venus", 8: "Mars", 9: "Jupiter", 10: "Saturn", 11: "Saturn", 12: "Jupiter"
}

# Add Rahu/Ketu planetary IDs for advanced aspect checks
swe.RAHU, swe.KETU = 11, 12
PLANETS_MAP = {"Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS, "Saturn": swe.SATURN, "Jupiter": swe.JUPITER}

# =====================================================================
# 2. CORE MATHEMATICS & DIVISIONAL EXTRACTION
# =====================================================================
def get_divisional_positions(total_longitude):
    d1_sign = int(total_longitude / 30.0) + 1
    d1_deg = total_longitude % 30.0
    
    pada_span = 30.0 / 9.0
    d9_sign = (int(total_longitude / pada_span) % 12) + 1
    d9_deg = (total_longitude % pada_span) * 9.0
    
    nak_span = 360.0 / 27.0
    nak_deg = total_longitude % nak_span
    
    return {
        "Total": total_longitude, "D1_Sign": d1_sign, "D1_Deg": d1_deg,
        "D9_Sign": d9_sign, "D9_Deg": d9_deg, "Nak_Deg": nak_deg
    }

def calculate_chart_vector(date_str, time_str, tz_offset, lat, lon, alt):
    base_dt = datetime.datetime.strptime(f"{date_str} {time_str}", "%Y.%m.%d %H:%M:%S")
    utc_dt = base_dt - datetime.timedelta(hours=tz_offset)
    jd_ut = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, utc_dt.hour + utc_dt.minute/60.0 + utc_dt.second/3600.0)
    
    swe.set_topo(lon, lat, alt)
    ayan = swe.get_ayanamsa_ut(jd_ut)
    
    cusps, ascmc = swe.houses(jd_ut, lat, lon, b'T')
    vector = {"Ascendant": get_divisional_positions((ascmc[0] - ayan) % 360)}
    
    for name, pid in PLANETS_MAP.items():
        res, f = swe.calc_ut(jd_ut, pid, swe.FLG_SIDEREAL | swe.FLG_TOPOCTR)
        vector[name] = get_divisional_positions(res[0])
    return vector

# =====================================================================
# 3. ASPECT & SENTIMENT ENGINES
# =====================================================================
def evaluate_aspects(t_name, t_sign, target_sign):
    """Calculates custom Vedic Drishti parameters based on sign distance."""
    # Compute sign distance (1-indexed counter)
    dist = (target_sign - t_sign) % 12 + 1
    
    if t_name == "Jupiter" and dist in [5, 7, 9]: return "asp"
    if t_name == "Mars" and dist in [4, 7, 8]: return "asp"
    if t_name == "Saturn" and dist in [3, 7, 10]: return "asp"
    if t_name in ["Sun", "Moon", "Venus", "Mercury"] and dist == 7: return "asp"
    if t_name in ["Rahu", "Ketu"] and dist in [5, 9]: return "asp"
    return None

def determine_sentiment_bias(asc_sign):
    """Maps dynamic sentiment scoring based on structural house ownership."""
    # 1st House is the current Ascendant sign, loop to find others
    house_to_sign = {h: (asc_sign + h - 2) % 12 + 1 for h in range(1, 13)}
    
    bull_planets = [SIGN_LORDS[house_to_sign[h]] for h in [5, 9, 11]]
    bear_planets = [SIGN_LORDS[house_to_sign[h]] for h in [6, 8, 12]] # Corrected 5th to 6th house
    
    return set(bull_planets), set(bear_planets)

# =====================================================================
# 4. QUANTATIVE ANALYSIS PIPELINE
# =====================================================================
def run_market_execution_suite(market_date_str, market_tz):
    birth = calculate_chart_vector(DEFAULT_BIRTH_DATE, DEFAULT_BIRTH_TIME, DEFAULT_BIRTH_TZ, DEFAULT_LAT, DEFAULT_LON, DEFAULT_ALT)
    
    market_base = datetime.datetime.strptime(market_date_str, "%Y.%m.%d").date()
    current_local = datetime.datetime.combine(market_base, datetime.time(9, 0, 0))
    end_local = datetime.datetime.combine(market_base, datetime.time(16, 20, 0))
    
    logs = []
    
    while current_local <= end_local:
        time_str = current_local.strftime("%H:%M:%S")
        transit = calculate_chart_vector(market_date_str, time_str, market_tz, DEFAULT_LAT, DEFAULT_LON, DEFAULT_ALT)
        
        # Pull live sentiment blocks
        bull_lords, bear_lords = determine_sentiment_bias(transit["Ascendant"]["D1_Sign"])
        
        for t_name, t_pos in transit.items():
            # Rule 1: Check Cusp Crossovers
            if t_pos["D1_Deg"] <= BORDER_THRESHOLD_DEG or (30.0 - t_pos["D1_Deg"]) <= BORDER_THRESHOLD_DEG:
                logs.append({"Time": time_str, "Body": t_name, "Metric": "Sign Cusp Crossing", "Signal": "VOLATILITY"})
            if t_pos["Nak_Deg"] <= BORDER_THRESHOLD_DEG or ((360.0/27.0) - t_pos["Nak_Deg"]) <= BORDER_THRESHOLD_DEG:
                logs.append({"Time": time_str, "Body": t_name, "Metric": "Nakshatra Cusp Crossing", "Signal": "VOLATILITY"})
                
            # Rule 2: Inter-Chart Alignment
            for b_name, b_pos in birth.items():
                # Process D1 Matches
                if abs(t_pos["Total"] - b_pos["Total"]) <= PROXIMITY_ORBIT_DEG:
                    sig = "COLOR_RED_OBSERVE" if t_name == "Ascendant" else "CRITICAL_ENTRY"
                    logs.append({"Time": time_str, "Body": f"Market-{t_name}", "Metric": f"Conjoint Birth-{b_name} (D1)", "Signal": sig})
                # Process D9 Matches
                if abs(t_pos["D9_Deg"] - b_pos["D9_Deg"]) <= PROXIMITY_ORBIT_DEG and t_pos["D9_Sign"] == b_pos["D9_Sign"]:
                    sig = "COLOR_RED_OBSERVE" if t_name == "Ascendant" else "CRITICAL_ENTRY"
                    logs.append({"Time": time_str, "Body": f"Market-{t_name}", "Metric": f"Conjoint Birth-{b_name} (D9)", "Signal": sig})
                    
                # Rule 3: Compute Aspects (Drishti)
                aspect_hit = evaluate_aspects(t_name, t_pos["D1_Sign"], b_pos["D1_Sign"])
                if aspect_hit:
                    # Apply Sentiment Labels to the Aspect
                    bias = "BULL" if t_name in bull_lords else ("BEAR" if t_name in bear_lords else "NEUTRAL")
                    logs.append({"Time": time_str, "Body": t_name, "Metric": f"asp -> Birth-{b_name}", "Signal": bias})
                    
        current_local += datetime.timedelta(minutes=1)
        
    return pd.DataFrame(logs).drop_duplicates()

if __name__ == "__main__":
    df_market_signals = run_market_execution_suite("2026.06.15", market_tz=2.0)
    print(df_market_signals.head(20).to_string(index=False))
