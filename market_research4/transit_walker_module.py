from datetime import timedelta
from d1d9_core_module import get_chart_data

class TransitWalker:
    def __init__(self, input_hub):
        """
        The Hub (input_hub) provides the location and start time.
        """
        self.hub = input_hub

    def walk(self, duration_days=7, interval_minutes=5):
        """
        Generator that yields a transit chart snapshot at every interval.
        """
        current_dt = self.hub.dt_transit_start
        end_dt = current_dt + timedelta(days=duration_days)
        delta = timedelta(minutes=interval_minutes)
        
        while current_dt < end_dt:
            # Generate the chart snapshot using the Core Module
            chart_snapshot = get_chart_data(current_dt, self.hub)
            
            # Yield the data to the scanner/main module
            yield current_dt, chart_snapshot
            
            # Increment time
            current_dt += delta
