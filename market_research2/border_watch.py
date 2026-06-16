import swisseph as swe
import pandas as pd
from datetime import datetime, timedelta

# --- SETTINGS ---
swe.set_sid_mode(swe.SIDM_LAHIRI)
RASHI_BUFFER = 1.0 
NAK_BUFFER = 20 / 60.0 
STEP_MINUTES = 2

PLANETS = {
    "Sun": swe.SUN, "M": swe.MOON, "Mar": swe.MARS, "Mer": swe.MERCURY, 
    "Ven": swe.VENUS, "Jup": swe.JUPITER, "Sat": swe.SATURN
}

RASHIS = ["Ar","Ta","Ge","Cn","Le","Vi","Li","Sc","Sg","Cp","Aq","Pi"]

NAK_MAP = {
    "Ashwini": "Ashw", "Bharani": "Bhar", "Krittika": "Krit", "Rohini": "Rohi", 
    "Mrigashira": "Mrig", "Ardra": "Ardr", "Punarvasu": "Puna", "Pushya": "Push", 
    "Ashlesha": "Ashl", "Magha": "Magh", "Purva Phalguni": "PPha", 
    "Uttara Phalguni": "UPha", "Hasta": "Hast", "Chitra": "Chit", "Swati": "Swat", 
    "Vishakha": "Vish", "Anuradha": "Anur", "Jyeshtha": "Jyes", "Mula": "Mula", 
    "Purva Ashadha": "PAsh", "Uttara Ashadha": "UAsh", "Shravana": "Shra", 
    "Dhanishta": "Dhan", "Shatabhisha": "Shat", "Purva Bhadrapada": "PBha", 
    "Uttara Bhadrapada": "UBha", "Revati": "Reva"
}
NAK_NAMES = list(NAK_MAP.values())
NAK_SIZE = 13.333333333333333

def get_sidereal_data(jd, planet_id):
    res = swe.calc_ut(jd, planet_id, swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED)
    return res[0][0], res[0][3] < 0

def format_duration(delta):
    total = int(delta.total_seconds() / 60)
    return f"{total // 60}h {total % 60}m"

def rashi_zone(pos):
    p = pos % 30.0
    if p <= RASHI_BUFFER:
        s = int(pos // 30)
        return True, f"{RASHIS[(s-1)%12]}→{RASHIS[s%12]}"
    if p >= (30.0 - RASHI_BUFFER):
        s = int(pos // 30)
        return True, f"{RASHIS[s%12]}→{RASHIS[(s+1)%12]}"
    return False, None

def nak_zone(pos):
    p = pos % NAK_SIZE
    if p <= NAK_BUFFER:
        n = int(pos / NAK_SIZE)
        return True, f"{NAK_NAMES[(n-1)%27]}→{NAK_NAMES[n%27]}"
    if p >= (NAK_SIZE - NAK_BUFFER):
        n = int(pos / NAK_SIZE)
        return True, f"{NAK_NAMES[n%27]}→{NAK_NAMES[(n+1)%27]}"
    return False, None

def scan_transitions(start_dt, end_dt, name, pid, z_type):
    rows, in_z, entry, last, z_name = [], False, None, None, None
    curr = start_dt
    while curr <= end_dt:
        jd = swe.julday(curr.year, curr.month, curr.day, curr.hour + curr.minute/60.0)
        pos, is_retro = get_sidereal_data(jd, pid)
        p_name = f"{name}R" if is_retro else name
        
        inside, b = rashi_zone(pos) if z_type == "Rashi" else nak_zone(pos)
        if inside:
            if not in_z: in_z, entry, z_name = True, curr, b
            last = curr
        elif in_z:
            rows.append({"Planet": p_name, "Type": z_type, "Boundary": z_name, "Entry": entry.strftime("%d %H:%M"), "Exit": last.strftime("%d %H:%M"), "Dur": format_duration(last - entry)})
            in_z = False
        curr += timedelta(minutes=STEP_MINUTES)
    return rows

def generate_transition_report(start, end):
    rows = []
    for n, i in PLANETS.items():
        rows.extend(scan_transitions(start, end, n, i, "Rashi"))
        rows.extend(scan_transitions(start, end, n, i, "Nak"))
    df = pd.DataFrame(rows)
    return df.sort_values("Entry") if not df.empty else df

# Execution and Moon-specific Styling
df = generate_transition_report(datetime(2026, 6, 1), datetime(2026, 6, 30))

def style_moon(df):
    # Grey out rows where Planet is 'M' or 'MR'
    return df.style.apply(lambda row: ['color: grey' if row['Planet'] in ['M', 'MR'] else 'color: white' for _ in row], axis=1)

# Displaying with dark-mode friendly formatting
display(style_moon(df))
