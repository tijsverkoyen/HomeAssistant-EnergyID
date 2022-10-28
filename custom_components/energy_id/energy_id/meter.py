class EnergyIDMeter:
    def __init__(
            self,
            id: str,
            record_id: str,
            name: str,
            meter_type: str,
            metric: str,
            multiplier: float,
            reading_type: str,
            theme: str,
            unit: str
    ):
        self.id = id
        self.record_id = record_id
        self.name = name
        self.meter_type = meter_type
        self.metric = metric
        self.multiplier = multiplier
        self.reading_type = reading_type
        self.theme = theme
        self.unit = unit
        self.state = None
        self.last_updated = None
        self.last_updated_str = None
