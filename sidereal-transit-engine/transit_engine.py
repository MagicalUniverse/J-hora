import datetime
import swisseph as swe
import pandas as pd

# =====================================================================
# 1. BASELINE DEFAULTS (Oslo Profile from Image Lock)
# =====================================================================
DEFAULT_LAT = 59.90870  
DEFAULT_LON = 10.74779  
DEFAULT_ALT = 25.0      

swe.set_sid_mode(swe.SIDM_LAHIRI)
BORDER_THRESHOLD_DEG = 1.0 / 60.0  # 1 arcminute safety threshold

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigasira", "Ardra", 
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", 
    "Hasta", "Chitra", "Swati", "Visakha", "Anuradha", "Jyeshtha", 
    "Moola", "Purva Ashadha", "Uttara Ashadha", "Sravana", "Dhanishta", "Shatabhisha", 
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

# =====================================================================
# 2. CALCULATION CORE
# =====================================================================
def get_varga_indices(total_longitude):
    d1_index = int(total_longitude / 30.0)
    pada_span = 30.0 / 9.0
    d9_index = int(total_longitude / pada_span)
    return d1_index, d9_index

def check_border_details(deg_within_block, block_size):
    return (deg_within_block <= BORDER_THRESHOLD_DEG) or ((block_size - deg_within_block) <= BORDER_THRESHOLD_DEG)

def get_astronomical_profile(total_longitude):
    alerts = []
    d1_sign = int(total_longitude / 30) + 1
    d1_deg = total_longitude % 30
    if check_border_details(d1_deg, 30.0): alerts.append("D1 Rashi")
        
    pada_span = 30.0 / 9.0
    d9_sign = (int(total_longitude / pada_span) % 12) + 1
    d9_deg = total_longitude % pada_span
    if check_border_details(d9_deg, pada_span): alerts.append("D9/Pada")
        
    nak_span = 360.0 / 27.0
    nak_index = int(total_longitude / nak_span)
    nak_deg = total_longitude % nak_span
    
    status = f"[ALERT] Edge Boundary" if alerts else "OK"
        
    return {
        "D1_Sign": d1_sign, "D1_Deg": round(d1_deg, 4),
        "D9_Sign": d9_sign, "D9_Deg": round(d9_deg * 9.0, 4),
        "Nakshatra": NAKSHATRAS[nak_index % 27], "Status": status
    }

def get_lagna_longitude(dt_utc, lat, lon, alt):
    hour_utc = dt_utc.hour + (dt_utc.minute / 60.0) + (dt_utc.second / 3600.0)
    jd_ut = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, hour_utc)
    swe.set_topo(lon, lat, alt)
    ayan_offset = swe.get_ayanamsa_ut(jd_ut)
    cusps, ascmc = swe.houses(jd_ut, lat, lon, b'T')
    return (ascmc[0] - ayan_offset) % 360

def calculate_full_snapshot(dt_utc, tz_offset, event_reason, lat, lon, alt):
    hour_utc = dt_utc.hour + (dt_utc.minute / 60.0) + (dt_utc.second / 3600.0)
    jd_ut = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, hour_utc)
    swe.set_topo(lon, lat, alt)
    ayan_offset = swe.get_ayanamsa_ut(jd_ut)
    
    local_dt = dt_utc + datetime.timedelta(hours=tz_offset)
    timestamp_str = local_dt.strftime("%Y-%m-%d %H:%M:%S")
    
    cusps, ascmc = swe.houses(jd_ut, lat, lon, b'T')
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
# 3. RANGE SCANNER PIPELINE (With Location Support)
# =====================================================================
def run_adaptive_market_scan(target_date_str, tz_offset, track_varga="D9", lat=None, lon=None, alt=None):
    """Executes a single-day market session scan using precise parameters."""
    run_lat = lat if lat is not None else DEFAULT_LAT
    run_lon = lon if lon is not None else DEFAULT_LON
    run_alt = alt if alt is not None else DEFAULT_ALT

    base_date = datetime.datetime.strptime(target_date_str, "%Y.%m.%d").date()
    start_local = datetime.datetime.combine(base_date, datetime.time(9, 0, 0))
    end_local = datetime.datetime.combine(base_date, datetime.time(16, 20, 0))
    
    current_local = start_local
    all_outputs = []
    
    init_utc = current_local - datetime.timedelta(hours=tz_offset)
    last_lon = get_lagna_longitude(init_utc, run_lat, run_lon, run_alt)
    last_d1, last_d9 = get_varga_indices(last_lon)
    
    while current_local <= end_local:
        current_utc = current_local - datetime.timedelta(hours=tz_offset)
        current_lon = get_lagna_longitude(current_utc, run_lat, run_lon, run_alt)
        current_d1, current_d9 = get_varga_indices(current_lon)
        
        crossed = False
        reason = ""
        
        if track_varga == "D1" and current_d1 != last_d1:
            crossed = True
            reason = f"D1 Ascendant Shift"
        elif track_varga == "D9" and current_d9 != last_d9:
            crossed = True
            reason = f"D9 Ascendant Shift"
            
        if crossed:
            snapshot = calculate_full_snapshot(current_utc, tz_offset, reason, run_lat, run_lon, run_alt)
            all_outputs.extend(snapshot)
            last_d1, last_d9 = current_d1, current_d9
            
        last_lon = current_lon
        current_local += datetime.timedelta(minutes=1)
        
    return pd.DataFrame(all_outputs)

def run_multi_day_batch(start_date_str, end_date_str, tz_offset, track_varga="D9", lat=None, lon=None, alt=None):
    """Loops through a sequential date range to compile cross-over events."""
    start = datetime.datetime.strptime(start_date_str, "%Y.%m.%d").date()
    end = datetime.datetime.strptime(end_date_str, "%Y.%m.%d").date()
    delta = end - start
    
    master_frames = []
    for i in range(delta.days + 1):
        date_loop_str = (start + datetime.timedelta(days=i)).strftime("%Y.%m.%d")
        day_df = run_adaptive_market_scan(date_loop_str, tz_offset, track_varga, lat, lon, alt)
        if not day_df.empty:
            master_frames.append(day_df)
            
    return pd.concat(master_frames, ignore_index=True) if master_frames else pd.DataFrame()

# =====================================================================
# 4. EXECUTION CONTROL
# =====================================================================
if __name__ == "__main__":
    # Example: Run a multi-day test range with custom geographic settings
    df_results = run_multi_day_batch(
        start_date_str="2026.06.15", 
        end_date_str="2026.06.17", 
        tz_offset=2.0, 
        track_varga="D9",
        lat=59.90870,   # Set to None to default to Oslo
        lon=10.74779,
        alt=25.0
    )
    print(df_results[["Timestamp_Local", "Event", "Body", "D1_Sign", "D1_Deg", "D9_Sign", "D9_Deg"]].head(10))
