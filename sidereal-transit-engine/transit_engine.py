!pip install pyswisseph
import datetime
import swisseph as swe
import pandas as pd

# =====================================================================
# 1. FIXED PARAMETERS & TOPOCENTRIC COORDINATE LOCK
# =====================================================================
DEFAULT_LAT = 59.90870  # 59°54'31.31"N
DEFAULT_LON = 10.74779  # 10°44'52.06"E
DEFAULT_ALT = 25.0      # 25m Elevation

swe.set_sid_mode(swe.SIDM_LAHIRI)
BORDER_THRESHOLD_DEG = 1.0 / 60.0  # 1 arcminute safety margin

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigasira", "Ardra", 
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", 
    "Hasta", "Chitra", "Swati", "Visakha", "Anuradha", "Jyeshtha", 
    "Moola", "Purva Ashadha", "Uttara Ashadha", "Sravana", "Dhanishta", "Shatabhisha", 
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

# =====================================================================
# 2. CALCULATION ENGINE & PROFILER
# =====================================================================
def get_varga_indices(total_longitude):
    """Returns absolute integer blocks for D1 (0-11) and D9 (0-107) to detect flips."""
    d1_index = int(total_longitude / 30.0)
    pada_span = 30.0 / 9.0
    d9_index = int(total_longitude / pada_span)
    return d1_index, d9_index

def check_border_details(deg_within_block, block_size):
    return (deg_within_block <= BORDER_THRESHOLD_DEG) or ((block_size - deg_within_block) <= BORDER_THRESHOLD_DEG)

def get_astronomical_profile(total_longitude):
    alerts = []
    
    # D1 Rashi
    d1_sign = int(total_longitude / 30) + 1
    d1_deg = total_longitude % 30
    if check_border_details(d1_deg, 30.0): alerts.append("D1 Rashi")
        
    # D9 Navamsa
    pada_span = 30.0 / 9.0
    d9_sign = (int(total_longitude / pada_span) % 12) + 1
    d9_deg = total_longitude % pada_span
    if check_border_details(d9_deg, pada_span): alerts.append("D9/Pada")
        
    # D2 Hora
    d2_deg = total_longitude % 15.0
    if check_border_details(d2_deg, 15.0): alerts.append("D2 Hora")
        
    # Nakshatra
    nak_span = 360.0 / 27.0
    nak_index = int(total_longitude / nak_span)
    nak_deg = total_longitude % nak_span
    if check_border_details(nak_deg, nak_span): alerts.append("Nakshatra")
    
    pada_no = int(nak_deg / pada_span) + 1
    status = f"[ALERT] Verify: {', '.join(alerts)}" if alerts else "OK"
        
    return {
        "D1_Sign": d1_sign,
        "D1_Deg": round(d1_deg, 4),
        "D9_Sign": d9_sign,
        "D9_Deg": round(d9_deg * 9.0, 4), # Scaled back to 30° format for parity
        "Nakshatra": f"{NAKSHATRAS[nak_index % 27]} (P{pada_no})",
        "Status": status
    }

def get_lagna_longitude(dt_utc):
    """Isolates and returns the raw sidereal Lagna longitude for boundary checks."""
    hour_utc = dt_utc.hour + (dt_utc.minute / 60.0) + (dt_utc.second / 3600.0)
    jd_ut = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, hour_utc)
    swe.set_topo(DEFAULT_LON, DEFAULT_LAT, DEFAULT_ALT)
    ayan_offset = swe.get_ayanamsa_ut(jd_ut)
    cusps, ascmc = swe.houses(jd_ut, DEFAULT_LAT, DEFAULT_LON, b'T')
    return (ascmc[0] - ayan_offset) % 360

def calculate_full_snapshot(dt_utc, tz_offset, event_reason):
    """Generates complete D1 and D9 datasets for all tracked bodies at the target second."""
    hour_utc = dt_utc.hour + (dt_utc.minute / 60.0) + (dt_utc.second / 3600.0)
    jd_ut = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, hour_utc)
    swe.set_topo(DEFAULT_LON, DEFAULT_LAT, DEFAULT_ALT)
    ayan_offset = swe.get_ayanamsa_ut(jd_ut)
    
    local_dt = dt_utc + datetime.timedelta(hours=tz_offset)
    timestamp_str = local_dt.strftime("%Y-%m-%d %H:%M:%S")
    
    cusps, ascmc = swe.houses(jd_ut, DEFAULT_LAT, DEFAULT_LON, b'T')
    records = [{
        "Event": event_reason, "Timestamp_Local": timestamp_str, "Body": "Lagna", 
        **get_astronomical_profile((ascmc[0] - ayan_offset) % 360)
    }]
    
    PLANETS = {"Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS, "Saturn": swe.SATURN}
    for name, pid in PLANETS.items():
        res, f = swe.calc_ut(jd_ut, pid, swe.FLG_SIDEREAL | swe.FLG_TOPOCTR)
        records.append({
            "Event": event_reason, "Timestamp_Local": timestamp_str, "Body": name, 
            **get_astronomical_profile(res[0])
        })
    return records

# =====================================================================
# 3. ADAPTIVE FEEDBACK SCANNING LOOP
# =====================================================================
def run_adaptive_market_scan(target_date_str, tz_offset, track_varga="D9"):
    """
    Loops through market hours, detects structural ascendant crossovers, 
    and instantly triggers micro-window logging for both D1 and D9.
    """
    base_date = datetime.datetime.strptime(target_date_str, "%Y.%m.%d").date()
    start_local = datetime.datetime.combine(base_date, datetime.time(9, 0, 0))
    end_local = datetime.datetime.combine(base_date, datetime.time(16, 20, 0))
    
    current_local = start_local
    all_outputs = []
    
    # Initialize baseline coordinates
    init_utc = current_local - datetime.timedelta(hours=tz_offset)
    last_lon = get_lagna_longitude(init_utc)
    last_d1, last_d9 = get_varga_indices(last_lon)
    
    print(f"Beginning Adaptive Hunt on {target_date_str} for Ascendant {track_varga} flips...\n")
    
    while current_local <= end_local:
        current_utc = current_local - datetime.timedelta(hours=tz_offset)
        current_lon = get_lagna_longitude(current_utc)
        current_d1, current_d9 = get_varga_indices(current_lon)
        
        # Check if a boundary cross-over condition has been met
        crossed = False
        reason = ""
        
        if track_varga == "D1" and current_d1 != last_d1:
            crossed = True
            reason = f"D1 Ascendant Shift (Sign {last_d1+1} -> {current_d1+1})"
        elif track_varga == "D9" and current_d9 != last_d9:
            crossed = True
            reason = f"D9 Ascendant Shift (Block {last_d9} -> {current_d9})"
            
        if crossed:
            # FEEDBACK MECHANISM: Trigger complete structural log for this specific minute
            snapshot = calculate_full_snapshot(current_utc, tz_offset, reason)
            all_outputs.extend(snapshot)
            
            # Update state anchors
            last_d1 = current_d1
            last_d9 = current_d9
            
        # Standard step resolution: 1-minute tracking increments
        last_lon = current_lon
        current_local += datetime.timedelta(minutes=1)
        
    df_final = pd.DataFrame(all_outputs)
    return df_final

# =====================================================================
# 4. RUNTIME AUTOMATION CONTROL
# =====================================================================
if __name__ == "__main__":
    TARGET_DATE = "2026.06.15"
    TZ_OFFSET = 2.0  # Local time zone offset (GMT+2)
    
    # Change "D9" to "D1" if you only want to log when the major Rashi sign flips
    df_market_log = run_adaptive_market_scan(TARGET_DATE, TZ_OFFSET, track_varga="D9")
    
    # Save results to disk
    df_market_log.to_csv("final_output.csv", index=False)
    
    # Display preview rows
    print(df_market_log[["Timestamp_Local", "Event", "Body", "D1_Sign", "D1_Deg", "D9_Sign", "D9_Deg"]].head(15).to_string(index=False))
