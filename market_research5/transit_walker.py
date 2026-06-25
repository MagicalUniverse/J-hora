
# ============================================================
# SCRIPT NAME: transit_walker_module.py
# VERSION: 1.0.1
#
# REQUIREMENTS:
# 1. Consume configuration from input_module (via run_transit_walk arg).
# 2. Iterate through date/time ranges at defined interval steps.
# 3. Retrieve D1/D9 data for each step from d1d9_core_module.
# 4. Create and append data to a CSV file named by transit start date.
# 5. Ensure valid CSV structure with appropriate headers.
# ============================================================


import csv
from datetime import timedelta
from d1d9_core_module import get_chart_data

def run_transit_walk(cfg):
    """
    Generates 7-day transit data in 5-minute steps and saves to CSV.
    Version: 1.0.1
    """
    filename = f"transit_{cfg.dt_transit_start.strftime('%Y-%m-%d')}.csv"
    current_dt = cfg.dt_transit_start
    end_dt = cfg.dt_transit_start + timedelta(days=cfg.duration)
    step = timedelta(minutes=cfg.interval)
    
    with open(filename, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'body', 'd1_deg', 'd1_sign', 'd9_deg', 'd9_sign'])
        
        while current_dt <= end_dt:
            data = get_chart_data(cfg.lat, cfg.lon, current_dt)
            for row in data:
                writer.writerow([
                    current_dt.strftime('%Y-%m-%d %H:%M'),
                    row.get('body'),
                    row.get('d1_deg'),
                    row.get('d1_sign'),
                    row.get('d9_deg'),
                    row.get('d9_sign')
                ])
            current_dt += step
    return filename

