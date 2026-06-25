# SCRIPT NAME: main2_module.py
# VERSION: 3.0.0

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


# SCRIPT NAME: main2_module.py
# VERSION: 3.0.0

from datetime import datetime, timezone
from d1d9_core_module import get_chart_data

def print_birth_chart(year, month, day, hour, minute, second, lat, lon):
    """Prints formatted D1 and D9 chart data to the console."""
    dt = datetime(
        year,
        month,
        day,
        hour,
        minute,
        second,
        tzinfo=timezone.utc
    )

    chart = get_chart_data(lat=lat, lon=lon, dt=dt)

    print("=" * 60)
    print("BIRTH CHART VERIFICATION")
    print("=" * 60)
    print(f"Date/Time UTC : {dt}")
    print(f"Latitude      : {lat}")
    print(f"Longitude     : {lon}")
    print("-" * 60)
    print(
        f"{'Body':<8}"
        f"{'D1 Sign':<10}"
        f"{'D1 Deg':<12}"
        f"{'D9 Sign':<10}"
        f"{'D9 Deg':<12}"
    )
    print("-" * 60)

    for row in chart:
        print(
            f"{row['body']:<8}"
            f"{row['d1_sign']:<10}"
            f"{row['d1_deg']:<12}"
            f"{row['d9_sign']:<10}"
            f"{row['d9_deg']:<12}"
        )
    print("=" * 60)

if __name__ == "__main__":
    MY_LAT = 59.9139
    MY_LON = 10.7522

    print_birth_chart(
        1995,
        12,
        28,
        8,
        0,
        0,
        MY_LAT,
        MY_LON
    )
