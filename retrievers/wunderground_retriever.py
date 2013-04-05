__author__ = 'esteele'

from abstract_http_retriever import AbstractHTTPRetriever
import decimal
import datetime
import json


class WundergroundRetriever(AbstractHTTPRetriever):
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

    def generate_observation_request_for_location(self, location):
        return "http://api.wunderground.com/api/%s" \
               "/conditions/q/%s/%s.json" % (self.api_key,
                                             location.WUNDERGROUND_MAJOR_LOC,
                                             location.WUNDERGROUND_MINOR_LOC)

    def parse_observation_result_for_temperature(self, result):
        most_recent_ob = json.loads(
            result, parse_int=decimal.Decimal)["current_observation"]
        ob_datetime = datetime.datetime.fromtimestamp(
            float(most_recent_ob["local_epoch"]))
        return ob_datetime, most_recent_ob["temp_c"]

