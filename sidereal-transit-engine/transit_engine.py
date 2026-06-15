import datetime
import swisseph as swe
import pandas as pd

# =====================================================================
# 1. DEFAULT RADIX (BIRTH) & GEOGRAPHIC PARAMETERS
# =====================================================================
DEFAULT_BIRTH_DATE = "1814.05.17"
DEFAULT_BIRTH_TIME = "12:27:12"
DEFAULT_BIRTH_TZ   = 0.0  # Defaulting birth input directly to UT/GMT baseline

# Default Coordinates (Topocentric Lock)
DEFAULT_LAT = 60.3011
DEFAULT_LON = 11.1717
DEFAULT_ALT = 25.0

swe.set_sid_mode(swe.SIDM_LAHIRI)
PROXIMITY_ORBIT_DEG = 0.05  # Trigger match if within ~3 arcminutes

PLANETS_MAP = {"Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS, "Saturn": swe.SATURN}

# =====================================================================
# 2. CALCULATION CORE & DIVISIONAL EXTRACTORS
# =====================================================================
def get_divisional_positions(total_longitude):
    """Isolates exact absolute degrees for D1 and D9 structures."""
    d1_deg = total_longitude % 30.0
    pada_span = 30.0 / 9.0
    d9_deg = (total_longitude % pada_span) * 9.0  # Scaled to 30° parity
    return {"D1": round(total_longitude, 4), "D9": round(d9_deg, 4)}

def calculate_chart_vector(date_str, time_str, tz_offset, lat, lon, alt):
    """Generates a complete astronomical snapshot for any given target space-time."""
    base_dt = datetime.datetime.strptime(f"{date_str} {time_str}", "%Y.%m.%d %H:%M:%S")
    utc_dt = base_dt - datetime.timedelta(hours=tz_offset)
    
    hour_utc = utc_dt.hour + (utc_dt.minute / 60.0) + (utc_dt.second / 3600.0)
    jd_ut = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, hour_utc)
    
    swe.set_topo(lon, lat, alt)
    ayan_offset = swe.get_ayanamsa_ut(jd_ut)
    
    # House Cusps for Lagna
    cusps, ascmc = swe.houses(jd_ut, lat, lon, b'T')
    lagna_sidereal = (ascmc[0] - ayan_offset) % 360
    
    vector = {"Lagna": get_divisional_positions(lagna_sidereal)}
    for name, pid in PLANETS_MAP.items():
        res, f = swe.calc_ut(jd_ut, pid, swe.FLG_SIDEREAL | swe.FLG_TOPOCTR)
        vector[name] = get_divisional_positions(res[0])
    return vector

# =====================================================================
# 3. INTER-CHART SCANNER PIPELINE
# =====================================================================
def analyze_interchart_transits(market_date_str, market_tz, radix_override=None):
    """
    Scans market hours against Radix positions. Generates user-defined 
    Rule A (+60m) or Rule B (±30m) windows upon collision detection.
    """
    # Fallback to default birth parameters if no override vector is passed
    radix = radix_override if radix_override is not None else calculate_chart_vector(
        DEFAULT_BIRTH_DATE, DEFAULT_BIRTH_TIME, DEFAULT_BIRTH_TZ, DEFAULT_LAT, DEFAULT_LON, DEFAULT_ALT
    )
    
    market_base = datetime.datetime.strptime(market_date_str, "%Y.%m.%d").date()
    start_local = datetime.datetime.combine(market_base, datetime.time(9, 0, 0))
    end_local = datetime.datetime.combine(market_base, datetime.time(16, 20, 0))
    
    current_local = start_local
    triggered_events = []
    
    while current_local <= end_local:
        # Calculate current active transit profile
        time_str = current_local.strftime("%H:%M:%S")
        transit = calculate_chart_vector(market_date_str, time_str, market_tz, DEFAULT_LAT, DEFAULT_LON, DEFAULT_ALT)
        
        # Cross-compare transit data layers directly against our fixed birth vector
        for t_body, t_pos in transit.items():
            for r_body, r_pos in radix.items():
                
                # Check D1 Alignment
                if abs(t_pos["D1"] - r_pos["D1"]) <= PROXIMITY_ORBIT_DEG:
                    reason = f"Transit {t_body} Conjoint Radix {r_body} (D1)"
                    triggered_events.append({
                        "Match_Time": current_local.strftime("%Y-%m-%d %H:%M:%S"),
                        "Trigger": reason, "Layer": "D1 Macro"
                    })
                    
                # Check D9 Alignment
                if abs(t_pos["D9"] - r_pos["D9"]) <= PROXIMITY_ORBIT_DEG:
                    reason = f"Transit {t_body} Conjoint Radix {r_body} (D9)"
                    triggered_events.append({
                        "Match_Time": current_local.strftime("%Y-%m-%d %H:%M:%S"),
                        "Trigger": reason, "Layer": "D9 Micro"
                    })
                    
        current_local += datetime.timedelta(minutes=1)
        
    return pd.DataFrame(triggered_events).drop_duplicates(subset=["Trigger"])

# =====================================================================
# 4. RUNTIME VERIFICATION CONTROL
# =====================================================================
if __name__ == "__main__":
    print("--- RUNNING WITH DEFAULT HISTORICAL RADIX ---")
    df_defaults = analyze_interchart_transits("2026.06.15", market_tz=2.0)
    print(df_defaults.to_string(index=False) if not df_defaults.empty else "No structural radix connections hit today.")
    
    print("\n--- SAMPLE SHOWING USER REJECTION OF DEFAULT VALUES ---")
    # Custom user override parameters passed dynamically at runtime
    custom_radix = calculate_chart_vector(
        date_str="1990.01.01", time_str="06:00:00", tz_offset=1.0, 
        lat=57.1000, lon=12.2500, alt=0.0
    )
    df_overrides = analyze_interchart_transits("2026.06.15", market_tz=2.0, radix_override=custom_radix)
    print(df_overrides.to_string(index=False) if not df_overrides.empty else "No custom radix connections hit today.")
