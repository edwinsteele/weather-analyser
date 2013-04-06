from base_retrievers import AbstractRetriever
import decimal
import datetime
import json

__author__ = 'esteele'


class ForecastIoRetriever(AbstractRetriever):
    """
    https://developer.forecast.io/docs/v2

    "temperature": 22.53
    "time": 1364800423
    """
    def __init__(self, api_key):
        super(ForecastIoRetriever, self).__init__()
        self.api_key = api_key

    @property
    def source(self):
        return "Forecast.io"

    @property
    def observation_reload_delay(self):
        return 30

    def generate_observation_request_for_location(self, location):
        return "https://api.forecast.io/forecast/%s" \
               "/%s,%s?units=si" % (self.api_key,
                                    location.LAT,
                                    location.LON)

    def parse_observation_result_for_temperature(self, result):
        most_recent_ob = json.loads(
            result,
            parse_float=decimal.Decimal)["currently"]
        ob_datetime = datetime.datetime.fromtimestamp(
            float(most_recent_ob["time"]))
        return ob_datetime, most_recent_ob["temperature"]

