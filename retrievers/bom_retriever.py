from base_retrievers import AbstractRetriever
import decimal
import datetime
import json

__author__ = 'esteele'


class BOMRetriever(AbstractRetriever):
    """
    Observations:
    http://www.bom.gov.au/products/IDN60901/IDN60901.94768.shtml#other_formats

    local_date_time_full": "20130401180000"
    air_temp": 21.8

    URL format: IDQ60901

    Forecasts:
    http://www.bom.gov.au/info/precis_forecasts.shtml

    """
    def __init__(self):
        super(BOMRetriever, self).__init__()

    @property
    def source(self):
        return "BOM"

    @property
    def observation_reload_delay(self):
        return 30

    @property
    def forecast_reload_delay(self):
        raise NotImplementedError

    def generate_observation_request_for_location(self, location):
        return "http://www.bom.gov.au/fwo/ID%s60901/IDN60901.%s.json" % (
            location.BOM_STATE,
            location.BOM_STATION
        )

    def generate_forecast_request_for_location(self, location):
        raise NotImplementedError

    def parse_observation_response(self, result):
        most_recent_ob = json.loads(
            result, parse_float=decimal.Decimal)["observations"]["data"][0]
        ob_datetime = datetime.datetime.strptime(
            most_recent_ob["local_date_time_full"],
            "%Y%m%d%H%M%S")
        return ob_datetime, most_recent_ob["air_temp"]

    def parse_forecast_response(self, result):
        raise NotImplementedError
