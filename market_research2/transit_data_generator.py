import datetime
import swisseph as swe
import pandas as pd

# ==============================================================================
# GEOCENTRIC COORD LOCKED FRAMEWORK
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
    """Translates raw absolute longitudes strictly into Sign, Deg, Min, Sec."""
    norm_lon = total_longitude % 360.0
    sign = int(norm_lon / 30.0) + 1
    abs_deg = norm_lon % 30.0
    
    total_minutes = abs_deg * 60.0
    deg = int(abs_deg)
    minute = int(total_minutes)
    second = round((total_minutes - minute) * 60.0, 2)
    
    # Handle mathematical rounding overflow cascading boundaries
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

def generate_clean_dms_ledger(date_str, tz_offset):
    market_base = datetime.datetime.strptime(date_str, "%Y.%m.%d").date()
    current_local = datetime.datetime.combine(market_base, datetime.time(9, 0, 0))
    end_local = datetime.datetime.combine(market_base, datetime.time(16, 20, 0))
    records = []
    
    while current_local <= end_local:
        time_str = current_local.strftime("%H:%M:%S")
        utc_dt = current_local - datetime.timedelta(hours=tz_offset)
        decimal_hour = utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0
        jd_ut = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, decimal_hour)
        
        swe.set_topo(DEFAULT_LON, DEFAULT_LAT, DEFAULT_ALT)
        ayan = swe.get_ayanamsa_ut(jd_ut)
        _, ascmc = swe.houses(jd_ut, DEFAULT_LAT, DEFAULT_LON, b'T')
        
        # Core data assignments
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
    print(f"SUCCESS: Generated {output_name}")

# Execute calculations for the matrix
generate_clean_dms_ledger("2026.06.16", 5.5)
