import datetime
import swisseph as swe
import pandas as pd

# ==============================================================================
# GEOCENTRIC COORDINATE CONFIGURATION
# ==============================================================================
DEFAULT_LAT, DEFAULT_LON, DEFAULT_ALT = 60.3011, 11.1717, 25.0
swe.set_sid_mode(swe.SIDM_LAHIRI)
swe.RAHU, swe.KETU = 11, 12

PLANETS_MAP = {
    "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS,
    "Saturn": swe.SATURN, "Jupiter": swe.JUPITER, "Mercury": swe.MERCURY,
    "Venus": swe.VENUS, "Rahu": swe.RAHU, "Ketu": swe.KETU
}

def deconstruct_to_dms(total_longitude):
    """Deconstructs absolute longitudes strictly into isolated Sign, Deg, Min, Sec arc layers."""
    norm_lon = total_longitude % 360.0
    sign = int(norm_lon / 30.0) + 1
    abs_deg = norm_lon % 30.0
    
    total_minutes = abs_deg * 60.0
    deg = int(abs_deg)
    minute = int(total_minutes)
    second = round((total_minutes - minute) * 60.0, 2)
    
    if second >= 60.0:
        second = 0.0
        minute += 1
    if minute >= 60:
        minute = 0
        deg += 1
    if deg >= 30:
        deg = 0
        sign = (sign % 12) + 1
        
    return {"Sign": sign, "Deg": deg, "Min": minute, "Sec": second}

def calculate_single_day(target_date_obj, tz_offset):
    """Generates the absolute 441-minute tracking matrix for a verified session day."""
    date_str = target_date_obj.strftime("%Y.%m.%d")
    current_local = datetime.datetime.combine(target_date_obj, datetime.time(9, 0, 0))
    end_local = datetime.datetime.combine(target_date_obj, datetime.time(16, 20, 0))
    records = []
    
    while current_local <= end_local:
        time_str = current_local.strftime("%H:%M:%S")
        utc_dt = current_local - datetime.timedelta(hours=tz_offset)
        decimal_hour = utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0
        jd_ut = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, decimal_hour)
        
        swe.set_topo(DEFAULT_LON, DEFAULT_LAT, DEFAULT_ALT)
        ayan = swe.get_ayanamsa_ut(jd_ut)
        _, ascmc = swe.houses(jd_ut, DEFAULT_LAT, DEFAULT_LON, b'T')
        
        transit = {"Ascendant": deconstruct_to_dms((ascmc[0] - ayan) % 360.0)}
        for name, pid in PLANETS_MAP.items():
            res, _ = swe.calc_ut(jd_ut, pid, swe.FLG_SIDEREAL | swe.FLG_TOPOCTR)
            transit[name] = deconstruct_to_dms(res[0])
            
        row = {"Time": time_str}
        for name, pos in transit.items():
            row[f"{name}Sign"] = pos["Sign"]
            row[f"{name}Deg"] = pos["Deg"]
            row[f"{name}Min"] = pos["Min"]
            row[f"{name}Sec"] = pos["Sec"]
            
        records.append(row)
        current_local += datetime.timedelta(minutes=1)
        
    df = pd.DataFrame(records)
    output_name = f"ledger_{date_str}.csv"
    df.to_csv(output_name, index=False)
    print(f" -> SUCCESS: Exported {output_name}")

def generate_weekly_range(start_date_str, end_date_str, tz_offset=5.5):
    """Iterates through calendar dates, automatically dropping weekends."""
    start_date = datetime.datetime.strptime(start_date_str, "%Y.%m.%d").date()
    end_date = datetime.datetime.strptime(end_date_str, "%Y.%m.%d").date()
    
    print(f"=== INITIALIZING BATCH RUN FROM {start_date_str} TO {end_date_str} ===")
    current_date = start_date
    
    while current_date <= end_date:
        # 5 = Saturday, 6 = Sunday in Python's weekday model
        if current_date.weekday() >= 5:
            print(f"Skipping weekend date: {current_date.strftime('%Y.%m.%d')} (Market Closed)")
        else:
            calculate_single_day(current_date, tz_offset)
        current_date += datetime.timedelta(days=1)
        
    print("\n=== COMPLETE: ALL LEDGERS CREATED ===")

# Run the entire 5-day week in a single operation
generate_weekly_range(start_date_str="2026.06.15", end_date_str="2026.06.19")
