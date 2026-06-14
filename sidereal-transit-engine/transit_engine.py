import swisseph as swe
import pandas as pd

LATITUDE, LONGITUDE = 57.1000, 12.2500
swe.set_sid_mode(swe.SIDM_LAHIRI)
BORDER_THRESHOLD_DEG = 1.0 / 60.0  # 1 arcminute

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigasira", "Ardra", 
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", 
    "Hasta", "Chitra", "Swati", "Visakha", "Anuradha", "Jyeshtha", 
    "Moola", "Purva Ashadha", "Uttara Ashadha", "Sravana", "Dhanishta", "Shatabhisha", 
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

def check_border_details(deg_within_block, block_size):
    return (deg_within_block <= BORDER_THRESHOLD_DEG) or ((block_size - deg_within_block) <= BORDER_THRESHOLD_DEG)

def get_astronomical_profile(total_longitude):
    alerts = []
    
    # 1. Rashi (30°)
    d1_deg = total_longitude % 30
    if check_border_details(d1_deg, 30.0): alerts.append("D1 Rashi")
        
    # 2. Navamsa / Pada (3°20')
    pada_span = 30.0 / 9.0
    d9_deg = total_longitude % pada_span
    if check_border_details(d9_deg, pada_span): alerts.append("D9/Pada")
        
    # 3. Hora (15°)
    d2_deg = total_longitude % 15.0
    if check_border_details(d2_deg, 15.0): alerts.append("D2 Hora")
        
    # 4. Nakshatra (13°20')
    nak_span = 360.0 / 27.0
    nak_index = int(total_longitude / nak_span)
    nak_deg = total_longitude % nak_span
    if check_border_details(nak_deg, nak_span): alerts.append("Nakshatra")
    
    pada_no = int(nak_deg / pada_span) + 1
    status = f"[ALERT] Verify: {', '.join(alerts)}" if alerts else "OK"
        
    return {
        "Position": f"{int(total_longitude/30)+1} Sign ({round(d1_deg,4)}°)",
        "Nakshatra": f"{NAKSHATRAS[nak_index % 27]} (P{pada_no})",
        "Status": status
    }

def process_date(year, month, day, hour_utc):
    jd = swe.julday(year, month, day, hour_utc)
    ayan_offset = swe.get_ayanamsa_ut(jd)
    cusps, ascmc = swe.houses(jd, LATITUDE, LONGITUDE, b'T')
    
    records = [{"Body": "Lagna", **get_astronomical_profile((ascmc[0] - ayan_offset) % 360)}]
    PLANETS = {"Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS, "Saturn": swe.SATURN}
    for name, pid in PLANETS.items():
        res, f = swe.calc_ut(jd, pid, swe.FLG_SIDEREAL)
        records.append({"Body": name, **get_astronomical_profile(res[0])})
    return pd.DataFrame(records)

# Run verification timestamp
process_date(2026, 6, 15, 12.0)
