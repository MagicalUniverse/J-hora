# transit_scanner_module.py
class TransitScanner:
    def __init__(self, birth_chart_data, orb=1.0):
        self.birth_chart = birth_chart_data
        self.orb = orb # The allowed margin of error (degrees)

    def scan(self, transit_chart):
        alerts = []
        for b_name, b_lon in self.birth_chart:
            for t_name, t_lon in transit_chart:
                # Simple degree-based check (or your specific logic)
                if abs(b_lon - t_lon) < self.orb:
                    alerts.append(f"{t_name} is conjunct {b_name}")
        return alerts
