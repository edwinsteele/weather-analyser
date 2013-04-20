__author__ = 'esteele'


class SingleForecast(object):
    DAILY_FORECAST_TYPE = "D"
    HOURLY_FORECAST_TYPE = "H"

    def __init__(self, source, forecast_type, start_datetime, end_datetime,
                 issue_datetime, temperature_min, temperature_max):
        self.source = source
        if forecast_type in (self.DAILY_FORECAST_TYPE,
                             self.HOURLY_FORECAST_TYPE):
            self.forecast_type = forecast_type
        else:
            raise ValueError("Invalid forecast type: '%s'" % (forecast_type,))
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
        self.issue_datetime = issue_datetime
        self.temperature_min = float(temperature_min)
        self.temperature_max = float(temperature_max)

    def print_summary(self):
        print "%s Forecast by %s at %s for period %s-%s: Min: %s Max: %s" % (
            self.forecast_type, self.source, self.issue_datetime,
            self.start_datetime, self.end_datetime,
            self.temperature_min, self.temperature_max
        )


class Observation(object):
    def __init__(self, source, observation_datetime, temperature):
        self.source = source
        self.observation_datetime = observation_datetime
        self.temperature = temperature

    def print_summary(self):
        print "%s: last observation result: time %s, air temp %s" % (
            self.source,
            self.observation_datetime,
            self.temperature)