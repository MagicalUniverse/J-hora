# ============================================================
# NOTE (IMPORTANT FOR ALL AI ASSISTANTS / FUTURE CHATS)
#
# - D1 calculation is based on Swiss Ephemeris (sidereal Lahiri)
# - Minor arc-minute deviations (3–6 min) vs JHora are acceptable
#   and likely due to ephemeris + time precision differences
#
# - D9 (Navamsha) MUST remain fixed using the current mapping
#   system verified against JHora output pattern.
#
# - DO NOT REPLACE NAVAMSHA LOGIC WITHOUT JHORA CROSS CHECK
# ============================================================
# ============================================================
# SCRIPT NAME: main2_module.py
# VERSION: 1.5.2
# 
# REQUIREMENTS:
# 1. Orchestrate chart calculations from d1d9_core_module.
# 2. Maintain strict D1/D9 symmetry in printed output.
# 3. Validate birth chart against JHORA_REFERENCE via jhora_validator.
# 4. Trigger transit_walker_module to record 5-min interval
#    transit data to a CSV file.
# 5. Avoid patching: logic must remain in modular, standalone files.
# ============================================================

import importlib
import sys
from datetime import timedelta
from input_module import InputModule
from d1d9_core_module import get_chart_data
import transit_walker_module
import jhora_validator

def format_row(row):
    """
    Maintains strict D1/D9 symmetry: Deg° Sign M'S''
    """
    d1_val = row.get('d1_deg', '')
    d1_parts = d1_val.split(' ', 1)
    d1_deg = d1_parts[0]
    d1_ms = d1_parts[1] if len(d1_parts) > 1 else ''
    d1_sign = row.get('d1_sign', '')
    d1_formatted = f"{d1_deg}° {d1_sign} {d1_ms}"
    
    d9_val = row.get('d9_deg', '')
    d9_parts = d9_val.split(' ', 1)
    d9_deg = d9_parts[0]
    d9_ms = d9_parts[1] if len(d9_parts) > 1 else ''
    d9_sign = row.get('d9_sign', '')
    d9_formatted = f"{d9_deg}° {d9_sign} {d9_ms}"
    
    return f"{row['body']:<10}{d1_formatted:<25}{d9_formatted:<25}"

def run():
    cfg = InputModule()
    header = "Body      D1 (Deg° Sign M'S'')     D9 (Deg° Sign M'S'')"
    
    t_start_dt = cfg.dt_transit_start
    end_dt = t_start_dt + timedelta(days=cfg.duration)
    
    print(f"Birth Time: {cfg.dt_birth.strftime('%Y-%m-%d %H:%M')}")
    
    # 1. Print Reports
    for label, date in [("BIRTH CHART", cfg.dt_birth), 
                        (f"TRANSIT START ({t_start_dt.strftime('%Y-%m-%d')})", t_start_dt),
                        (f"TRANSIT END ({end_dt.strftime('%Y-%m-%d')})", end_dt)]:
        
        print(f"\n{label:^45}")
        print(header)
        print("-" * 60)
        
        chart_data = get_chart_data(cfg.lat, cfg.lon, date)
        for row in chart_data:
            print(format_row(row))
            
        # Run validation only on the Birth Chart
        if label == "BIRTH CHART":
            jhora_validator.validate(chart_data, cfg.JHORA_REFERENCE)

    # 2. Trigger Transit Walker for CSV File Generation
    print("\n[INFO] Starting transit walker...")
    transit_walker_module.run_transit_walk(cfg)
    print("[INFO] Transit sequence generation complete.")

if __name__ == "__main__":
    run()
