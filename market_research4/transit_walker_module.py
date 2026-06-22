from datetime import timedelta
from d1d9_core import get_chart_data

class TransitWalker:
    def __init__(self, input_hub):
        self.hub = input_hub

    def walk(self, duration_days=7, interval_minutes=5):
        current_dt = self.hub.dt_transit_start
        end_dt = current_dt + timedelta(days=duration_days)
        delta = timedelta(minutes=interval_minutes)
        
        while current_dt < end_dt:
            # The core module calculates based on current time and hub settings
            chart_snapshot = get_chart_data(current_dt, self.hub)
            yield current_dt, chart_snapshot
            current_dt += delta
