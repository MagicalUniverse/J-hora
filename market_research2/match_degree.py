import swisseph as swe
import pandas as pd
from datetime import datetime, timedelta

swe.set_sid_mode(swe.SIDM_LAHIRI)
RASHIS = ["Ar", "Ta", "Ge", "Cn", "Le", "Vi", "Li", "Sc", "Sg", "Cp", "Aq", "Pi"]

NATAL_D1 = {"Sun": 51.41, "M": 297.14, "Mar": 19.48, "Mer": 73.42, "Jup": 90.87, "Ven": 87.46, "Sat": 348.45}
NATAL_D9 = {k: (v * 9) % 360 for k, v in NATAL_D1.items()}

def scan_full_transit(start_dt, days=5, orb=1.0):
    rows = []
    # Planets to scan
    bodies = {"Sun": swe.SUN, "M": swe.MOON, "Mar": swe.MARS, "Mer": swe.MERCURY, 
              "Jup": swe.JUPITER, "Ven": swe.VENUS, "Sat": swe.SATURN}
    
    # Scan both Transiting D1 and D9 against both Natal D1 and D9
    for trans_mode in ["d1", "d9"]:
        for body_name, pid in bodies.items():
            for nat_mode, nat_dict in [("d1", NATAL_D1), ("d9", NATAL_D9)]:
                for nat_name, nat_deg in nat_dict.items():
                    curr = start_dt
                    in_orb, entry = False, None
                    
                    while curr < start_dt + timedelta(days=days):
                        jd = swe.julday(curr.year, curr.month, curr.day, curr.hour + curr.minute/60.0)
                        pos, _ = swe.calc_ut(jd, pid, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)
                        
                        # Calculate Transiting position (D1 or D9)
                        trans_deg = pos[0] if trans_mode == "d1" else (pos[0] * 9) % 360
                        
                        if abs(trans_deg - nat_deg) <= (orb / 2):
                            if not in_orb: in_orb, entry = True, curr
                        elif in_orb:
                            rows.append({
                                "Trans": f"{trans_mode}-{body_name}",
                                "Match": f"{nat_mode}-{nat_name}",
                                "Entry": entry.strftime("%d %H:%M"),
                                "Exit": curr.strftime("%d %H:%M")
                            })
                            in_orb = False
                        curr += timedelta(minutes=2)
    return pd.DataFrame(rows).sort_values("Entry")

df = scan_full_transit(datetime(2026, 6, 16))
print(df.to_string(index=False))
