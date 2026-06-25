

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
# VERSION: 1.2.9
# PURPOSE: Strict output formatting with escaped quotes
# ============================================================


from datetime import timedelta
from input_module import InputModule
from d1d9_core_module import get_chart_data


def format_row(row):
    """
    Parses both D1 and D9 to ensure the format: Deg° Sign M'S''
    """
    # Process D1: Expects format like "19 54'48''"
    d1_val = row.get('d1_deg', '')
    d1_parts = d1_val.split(' ', 1)
    d1_deg = d1_parts[0]
    d1_ms = d1_parts[1] if len(d1_parts) > 1 else ''
    d1_formatted = f"{d1_deg}° {row.get('sign', '')} {d1_ms}"
   
    # Process D9: Expects format like "29 13'17''"
    # Assuming d9_deg is the degree/min/sec part and d9_sign is the sign
    d9_val = row.get('d9_deg', '')
    d9_parts = d9_val.split(' ', 1)
    d9_deg = d9_parts[0]
    d9_ms = d9_parts[1] if len(d9_parts) > 1 else ''
    d9_formatted = f"{d9_deg}° {row.get('d9_sign', '')} {d9_ms}"
   
    return f"{row['body']:<10}{d1_formatted:<25}{d9_formatted:<25}"


def run():
    cfg = InputModule()
   
    b_date = cfg.dt_birth.strftime('%Y-%m-%d %H:%M')
    t_start = cfg.dt_transit_start.strftime('%Y-%m-%d %H:%M')
    end_dt = cfg.dt_transit_start + timedelta(days=cfg.duration)
    t_end = end_dt.strftime('%Y-%m-%d %H:%M')
   
    print(f"Birth Time: {b_date}")
   
    # Using double quotes for the print strings to avoid quote conflict
    print(f"\n{'BIRTH CHART':^45}")
    print(f"{'Body':<10}{'D1 (Deg° Sign M\'S\'\')':<20}{'D9 (Sign M\'S\'\')':<20}")
    print("-" * 50)
   
    # We iterate and print
    for row in get_chart_data(cfg.lat, cfg.lon, cfg.dt_birth):
        print(format_row(row))


    print(f"\n{'TRANSIT START (' + t_start + ')':^45}")
    print(f"{'Body':<10}{'D1 (Deg° Sign M\'S\'\')':<20}{'D9 (Sign M\'S\'\')':<20}")
    print("-" * 50)
    for row in get_chart_data(cfg.lat, cfg.lon, cfg.dt_transit_start):
        print(format_row(row))


    print(f"\n{'TRANSIT END (' + t_end + ')':^45}")
    print(f"{'Body':<10}{'D1 (Deg° Sign M\'S\'\')':<20}{'D9 (Sign M\'S\'\')':<20}")
    print("-" * 50)
    for row in get_chart_data(cfg.lat, cfg.lon, end_dt):
        print(format_row(row))


if __name__ == "__main__":
    run()

