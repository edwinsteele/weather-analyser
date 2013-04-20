from base_retrievers import AbstractRetriever
from models import Observation, SingleForecast
import decimal
import datetime
import json

__author__ = 'esteele'


class WundergroundRetriever(AbstractRetriever):
    """
    http://www.wunderground.com/weather/api/d/docs

    "local_epoch":"1364800751"
    "temp_c":22
    """
    def __init__(self, api_key):
        super(WundergroundRetriever, self).__init__()
        self.api_key = api_key

    @property
    def source(self):
        return "Wunderground"

    @property
    def observation_reload_delay(self):
        return 30

    @property
    def forecast_reload_delay(self):
        return 60

    def generate_observation_request_for_location(self, location):
        return "http://api.wunderground.com/api/%s" \
               "/conditions/q/%s/%s.json" % (self.api_key,
                                             location.WUNDERGROUND_MAJOR_LOC,
                                             location.WUNDERGROUND_MINOR_LOC)

    def generate_forecast_request_for_location(self, location):
        # They have a different URL for hourly forecasts!
        return "http://api.wunderground.com/api/%s" \
               "/forecast10day/q/%s/%s.json" % (self.api_key,
                                                location.WUNDERGROUND_MAJOR_LOC,
                                                location.WUNDERGROUND_MINOR_LOC)

    def parse_observation_response(self, result):
        most_recent_ob = json.loads(
            result, parse_int=decimal.Decimal)["current_observation"]
        ob_datetime = datetime.datetime.fromtimestamp(
            float(most_recent_ob["local_epoch"]))
        return Observation(self.source, ob_datetime, most_recent_ob["temp_c"])

    def parse_forecast_response(self, result):
        forecast_results = []
        json_result = json.loads(
            result,
            parse_float=decimal.Decimal)
        issue_date_best_guess = datetime.datetime.now()  #XXX ????
        for daily_forecast in json_result["forecast"]["simpleforecast"]["forecastday"]:
            start_time = datetime.datetime.fromtimestamp(float(daily_forecast["date"]["epoch"]))
            issue_date_best_guess = min(issue_date_best_guess, start_time)  #????
            forecast_results.append(SingleForecast(
                self.source,
                SingleForecast.DAILY_FORECAST_TYPE,
                start_time,
                start_time + datetime.timedelta(hours=23, minutes=59),
                issue_date_best_guess,
                daily_forecast["low"]["celsius"],
                daily_forecast["high"]["celsius"]
            ))
        # Do hourly forecasts later
        return forecast_results
