from datetime import timedelta
from d1d9_core import get_chart_data

class TransitWalker:
    def __init__(self, start_dt, lat, lon):
        self.start_dt = start_dt
        self.lat = lat
        self.lon = lon

    def walk(self, duration_days=7, interval_minutes=5):
        """
        Generates chart data for a flexible duration and interval.
        """
        end_dt = self.start_dt + timedelta(days=duration_days)
        current_dt = self.start_dt
        delta = timedelta(minutes=interval_minutes)
        
        while current_dt < end_dt:
            # Generate the chart snapshot
            chart_snapshot = get_chart_data(current_dt, self.lat, self.lon)
            
            # Yield data to scanner
            yield current_dt, chart_snapshot
            
            # Increment time
            current_dt += delta
