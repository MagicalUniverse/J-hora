import datetime
import swisseph as swe
import pandas as pd

# ==============================================================================
# SYSTEM CONFIGURATION AND MASTER BASELINE LOCK
# ==============================================================================
DEFAULT_BIRTH_DATE = "1814.05.17"
DEFAULT_BIRTH_TIME = "12:27:12"
DEFAULT_BIRTH_TZ   = 0.0

DEFAULT_LAT = 60.3011
DEFAULT_LON = 11.1717
DEFAULT_ALT = 25.0

# Configure Lahiri Ayanamsa for Sidereal Accuracy
swe.set_sid_mode(swe.SIDM_LAHIRI)

# Hardcode Swiss Ephemeris IDs for Lunar Nodes
swe.RAHU, swe.KETU = 11, 12

# Full-Spectrum Planetary Roster
PLANETS_MAP = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mars": swe.MARS,
    "Saturn": swe.SATURN,
    "Jupiter": swe.JUPITER,
    "Mercury": swe.MERCURY,
    "Venus": swe.VENUS,
    "Rahu": swe.RAHU,
    "Ketu": swe.KETU
}

def get_fine_coordinates(total_longitude):
    """Deconstructs absolute longitude into granular Sign, Deg, Min, Sec arc layers."""
    sign = int(total_longitude / 30.0) + 1
    abs_deg = total_longitude % 30.0
    
    total_minutes = abs_deg * 60.0
    deg = int(abs_deg)
    
    total_seconds = (total_minutes - int(total_minutes)) * 60.0
    minute = int(total_minutes)
    second = round(total_seconds, 2)
    
    # D9 Micro Navamsa Layer Calculation (3°20' spans per Pada)
    pada_span = 30.0 / 9.0
    d9_sign = (int(total_longitude / pada_span) % 12) + 1
    d9_deg = (total_longitude % pada_span) * 9.0
    
    # Nakshatra Constellation Boundary Calculation (13°20' blocks)
    nak_span = 360.0 / 27.0
    nak_deg = total_longitude % nak_span
    
    return {
        "Total": round(total_longitude, 6), 
        "Sign": sign, 
        "Deg": deg, 
        "Min": minute, 
        "Sec": second,
        "D9_Sign": d9_sign, 
        "D9_Deg": round(d9_deg, 6), 
        "Nak_Deg": round(nak_deg, 6)
    }

def calculate_chart_vector(date_str, time_str, tz_offset, lat, lon, alt):
    """Computes coordinate positions using precise topocentric ephemeris models."""
    base_dt = datetime.datetime.strptime(f"{date_str} {time_str}", "%Y.%m.%d %H:%M:%S")
    utc_dt = base_dt - datetime.timedelta(hours=tz_offset)
    
    jd_ut = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, 
                      utc_dt.hour + utc_dt.minute/60.0 + utc_dt.second/3600.0)
    
    swe.set_topo(lon, lat, alt)
    ayan = swe.get_ayanamsa_ut(jd_ut)
    
    # Calculate Horizon Matrix (Houses & Ascendant)
    cusps, ascmc = swe.houses(jd_ut, lat, lon, b'T')
    vector = {"Ascendant": get_fine_coordinates((ascmc[0] - ayan) % 360)}
    
    # Loop dynamically through the complete planet map configuration
    for name, pid in PLANETS_MAP.items():
        res, f = swe.calc_ut(jd_ut, pid, swe.FLG_SIDEREAL | swe.FLG_TOPOCTR)
        vector[name] = get_fine_coordinates(res[0])
        
    return vector

def generate_raw_research_ledger(market_date_str, market_tz):
    """Generates an absolute coordinate ledger for every minute of the session."""
    market_base = datetime.datetime.strptime(market_date_str, "%Y.%m.%d").date()
    current_local = datetime.datetime.combine(market_base, datetime.time(9, 0, 0))
    end_local = datetime.datetime.combine(market_base, datetime.time(16, 20, 0))
    raw_records = []
    
    while current_local <= end_local:
        time_str = current_local.strftime("%H:%M:%S")
        transit = calculate_chart_vector(market_date_str, time_str, market_tz, DEFAULT_LAT, DEFAULT_LON, DEFAULT_ALT)
        
        row = {"Time": time_str}
        
        for t_name, t_pos in transit.items():
            row[f"M_{t_name}_Total"] = t_pos["Total"]
            row[f"M_{t_name}_Sign"] = t_pos["Sign"]
            row[f"M_{t_name}_Deg"] = t_pos["Deg"]
            row[f"M_{t_name}_Min"] = t_pos["Min"]
            row[f"M_{t_name}_Sec"] = t_pos["Sec"]
            row[f"M_{t_name}_D9_Sign"] = t_pos["D9_Sign"]
            row[f"M_{t_name}_D9_Deg"] = t_pos["D9_Deg"]
            row[f"M_{t_name}_Nak_Deg"] = t_pos["Nak_Deg"]
            
        raw_records.append(row)
        current_local += datetime.timedelta(minutes=1)
        
    return pd.DataFrame(raw_records)

import pandas as pd

# 1. Read the pristine starting configuration from your original file
with open("transit_data_generator.py", "r") as f:
    content = f.read()

# Isolate the configuration constants at the top
config_section = content.split("def get_fine_coordinates")[0]

# 2. Re-write the complete, repaired file from scratch with all data streams
complete_working_script = config_section + """def get_fine_coordinates(total_longitude):
    \"\"\"Deconstructs absolute longitude into granular Sign, Deg, Min, Sec arc layers.\"\"\"
    sign = int(total_longitude / 30.0) + 1
    abs_deg = total_longitude % 30.0
    
    total_minutes = abs_deg * 60.0
    deg = int(abs_deg)
    
    total_seconds = (total_minutes - int(total_minutes)) * 60.0
    minute = int(total_minutes)
    second = round(total_seconds, 2)
    
    # D9 Micro Layer
    pada_span = 30.0 / 9.0
    d9_sign = (int(total_longitude / pada_span) % 12) + 1
    d9_deg = (total_longitude % pada_span) * 9.0
    
    # Nakshatra Boundary
    nak_span = 360.0 / 27.0
    nak_deg = total_longitude % nak_span
    
    return {
        "Total": round(total_longitude, 6), "Sign": sign, "Deg": deg, "Min": minute, "Sec": second,
        "D9_Sign": d9_sign, "D9_Deg": round(d9_deg, 6), "Nak_Deg": round(nak_deg, 6)
    }

def calculate_chart_vector(date_str, time_str, tz_offset, lat, lon, alt):
    base_dt = datetime.datetime.strptime(f"{date_str} {time_str}", "%Y.%m.%d %H:%M:%S")
    utc_dt = base_dt - datetime.timedelta(hours=tz_offset)
    jd_ut = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, utc_dt.hour + utc_dt.minute/60.0 + utc_dt.second/3600.0)
    swe.set_topo(lon, lat, alt)
    ayan = swe.get_ayanamsa_ut(jd_ut)
    cusps, ascmc = swe.houses(jd_ut, lat, lon, b'T')
    vector = {"Ascendant": get_fine_coordinates((ascmc[0] - ayan) % 360)}
    for name, pid in PLANETS_MAP.items():
        res, f = swe.calc_ut(jd_ut, pid, swe.FLG_SIDEREAL | swe.FLG_TOPOCTR)
        vector[name] = get_fine_coordinates(res[0])
    return vector

def generate_raw_research_ledger(market_date_str, market_tz):
    market_base = datetime.datetime.strptime(market_date_str, "%Y.%m.%d").date()
    current_local = datetime.datetime.combine(market_base, datetime.time(9, 0, 0))
    end_local = datetime.datetime.combine(market_base, datetime.time(16, 20, 0))
    raw_records = []
    
    while current_local <= end_local:
        time_str = current_local.strftime("%H:%M:%S")
        transit = calculate_chart_vector(market_date_str, time_str, market_tz, DEFAULT_LAT, DEFAULT_LON, DEFAULT_ALT)
        row = {"Time": time_str}
        
        for t_name, t_pos in transit.items():
            row[f"M_{t_name}_Total"] = t_pos["Total"]
            row[f"M_{t_name}_Sign"] = t_pos["Sign"]
            row[f"M_{t_name}_Deg"] = t_pos["Deg"]
            row[f"M_{t_name}_Min"] = t_pos["Min"]
            row[f"M_{t_name}_Sec"] = t_pos["Sec"]
            row[f"M_{t_name}_D9_Sign"] = t_pos["D9_Sign"]
            row[f"M_{t_name}_D9_Deg"] = t_pos["D9_Deg"]
            row[f"M_{t_name}_Nak_Deg"] = t_pos["Nak_Deg"]
            
        raw_records.append(row)
        current_local += datetime.timedelta(minutes=1)
        
    return pd.DataFrame(raw_records)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        target_date = sys.argv[1]
    else:
        target_date = "2026.05.17"
        
    print(f"Generating granular ledger for target date: {target_date}...")
    df = generate_raw_research_ledger(target_date, 5.5)
    
    output_filename = f"ledger_{target_date}.csv"
    df.to_csv(output_filename, index=False)
    
    print(f"Success! Saved {len(df)} rows to '{output_filename}'")

# 3. Write the fully integrated code back to the file
with open("transit_data_generator.py", "w") as f:
    f.write(complete_working_script)

# 4. Execute the finished script
!python transit_data_generator.py
