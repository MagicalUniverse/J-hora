import swisseph as swe
import pandas as pd
from datetime import datetime, timedelta

swe.set_sid_mode(swe.SIDM_LAHIRI)

# --- SETTINGS ---
MATCH_MODE = 'STRICT' # Options: 'STRICT' (00-59m) or 'ORB' (+/- 0.5 deg)

NATAL_D1 = {"Sun": 51.41, "M": 297.14, "Mar": 19.48, "Mer": 73.42, "Jup": 90.87, "Ven": 87.46, "Sat": 348.45}
NATAL_D9 = {k: (v * 9) % 360 for k, v in NATAL_D1.items()}

def scan_transit(start_dt, end_dt, mode='STRICT'):
    rows = []
    bodies = {"Sun": swe.SUN, "M": swe.MOON, "Mar": swe.MARS, "Mer": swe.MERCURY, 
              "Jup": swe.JUPITER, "Ven": swe.VENUS, "Sat": swe.SATURN}
    
    for trans_mode in ["d1", "d9"]:
        for body_name, pid in bodies.items():
            # Exclude transiting d9-Moon to remove noise
            if trans_mode == "d9" and body_name == "M":
                continue
                
            for nat_mode, nat_dict in [("d1", NATAL_D1), ("d9", NATAL_D9)]:
                for nat_name, nat_deg in nat_dict.items():
                    curr = start_dt
                    in_match, entry = False, None
                    
                    # Scan between start_dt and end_dt
                    while curr < end_dt:
                        jd = swe.julday(curr.year, curr.month, curr.day, curr.hour + curr.minute/60.0)
                        pos, _ = swe.calc_ut(jd, pid, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)
                        
                        trans_deg = pos[0] if trans_mode == "d1" else (pos[0] * 9) % 360
                        
                        if mode == 'STRICT':
                            is_match = int(trans_deg) == int(nat_deg)
                        else:
                            is_match = abs(trans_deg - nat_deg) <= 0.5
                        
                        if is_match:
                            if not in_match: in_match, entry = True, curr
                        elif in_match:
                            rows.append({
                                "Trans": f"{trans_mode}-{body_name}",
                                "Match": f"{nat_mode}-{nat_name}",
                                "Entry": entry.strftime("%d %H:%M"),
                                "Exit": curr.strftime("%d %H:%M")
                            })
                            in_match = False
                        curr += timedelta(minutes=2)
    return pd.DataFrame(rows).sort_values("Entry")

def style_transit_df(df):
    def highlight_row(row):
        day = int(row['Entry'].split()[0])
        bg_color = '#f0f0f0' if day % 2 == 0 else '#ffffff'
        
        entry_time = row['Entry'].split()[1]
        exit_time = row['Exit'].split()[1]
        is_biz_hour = (entry_time <= "16:20") and (exit_time >= "09:00")
        
        return [f'background-color: {bg_color}; font-weight: {"bold" if is_biz_hour else "normal"}; color: {"#000000" if is_biz_hour else "#666666"}'] * len(row)
    return df.style.apply(highlight_row, axis=1)

# --- EXECUTION ---
# Simply update these two dates to define your scan range
start = datetime(2026, 6, 16)
end = datetime(2026, 6, 21)

df_results = scan_transit(start, end, mode=MATCH_MODE)
style_transit_df(df_results)
