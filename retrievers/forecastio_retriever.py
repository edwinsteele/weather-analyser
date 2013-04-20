from base_retrievers import AbstractRetriever
from models import Observation, SingleForecast
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

    @property
    def forecast_reload_delay(self):
        return 60

    def generate_observation_request_for_location(self, location):
        return "https://api.forecast.io/forecast/%s" \
               "/%s,%s?units=si" % (self.api_key,
                                    location.LAT,
                                    location.LON)

    def parse_observation_response(self, result):
        most_recent_ob = json.loads(
            result,
            parse_float=decimal.Decimal)["currently"]
        ob_datetime = datetime.datetime.fromtimestamp(
            float(most_recent_ob["time"]))
        return Observation(self.source, ob_datetime, most_recent_ob["temperature"])

    def generate_forecast_request_for_location(self, location):
        # forecast and observation are in the same request
        return self.generate_observation_request_for_location(location)

    def parse_forecast_response(self, result):
        """
        which day do we actually want, anyway?
        """
        forecast_results = []
        json_result = json.loads(
            result,
            parse_float=decimal.Decimal)
        issue_date_best_guess = datetime.datetime.fromtimestamp(
            json_result["currently"]["time"])
        for daily_forecast in json_result["daily"]["data"]:
            start_time = datetime.datetime.fromtimestamp(daily_forecast["time"])
            # Forecast.io don't provide an issue date, so let's just use the
            #  minimum timestamp that we come across.
            # The daily forecasts will have the most outdated forecast, so by
            #  processing them first, we should get the most accurate issue
            #  date estimate
            issue_date_best_guess = min(issue_date_best_guess, start_time)
            forecast_results.append(SingleForecast(
                self.source,
                SingleForecast.DAILY_FORECAST_TYPE,
                start_time,
                start_time + datetime.timedelta(hours=23, minutes=59),
                issue_date_best_guess,
                daily_forecast["temperatureMin"],
                daily_forecast["temperatureMax"]
            ))
            # Don't look at the hourly forecasts yet... they have a single
            #  temperature reading, so we'd put the min & max as the same value
            #  or derive it from the previous/next reading
        return forecast_results

