from twisted.internet import reactor
from twisted.web.client import getPage
import abc
import datetime
import decimal
import json
import os

__author__ = 'esteele'


def get_env_variable(var_name):
    """ Get the environment variable or return exception """
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = "Set the %s env variable" % var_name
        raise RuntimeError(error_msg)


class AbstractHTTPObservationRetriever(object):
    SOURCE = "Abstract Retriever"

    def __init__(self):
        self.last_temperature_info = (None, None)
        self.URL = None

    def retrieve_observation(self):
        return getPage(self.URL)

    def parse_result_for_temperature(self, result):
        raise NotImplementedError

    def print_error(self, failure):
        print "Fail:", failure

    def print_results_periodically(self, period_seconds):
        print "%s last result: time %s, air temp %s" % (
            self.SOURCE,
            self.last_temperature_info[0],
            self.last_temperature_info[1])
        reactor.callLater(period_seconds,
                          self.print_results_periodically,
                          period_seconds)

    def handle_observation(self, result):
        print "Handling ob for ", self.SOURCE
        # parse
        temperature_info = self.parse_result_for_temperature(result)
        # store
        self.last_temperature_info = temperature_info


class BOMObservationRetrieverAbstract(AbstractHTTPObservationRetriever):
    """
    http://www.bom.gov.au/products/IDN60901/IDN60901.94768.shtml#other_formats

    local_date_time_full": "20130401180000"
    air_temp": 21.8
    """
    SOURCE = "BOM"

    def __init__(self):
        super(BOMObservationRetrieverAbstract, self).__init__()
        self.URL = "http://www.bom.gov.au/fwo/IDN60901/IDN60901.94768.json"

    def parse_result_for_temperature(self, result):
        most_recent_ob = json.loads(
            result, parse_float=decimal.Decimal)["observations"]["data"][0]
        ob_datetime = datetime.datetime.strptime(
            most_recent_ob["local_date_time_full"],
            "%Y%m%d%H%M%S")
        return ob_datetime, most_recent_ob["air_temp"]


class WundergroundObservationRetrieverAbstract(AbstractHTTPObservationRetriever):
    """
    http://www.wunderground.com/weather/api/d/docs

    "local_epoch":"1364800751"
    "temp_c":22
    """
    SOURCE = "Wunderground"

    def __init__(self, api_key):
        super(WundergroundObservationRetrieverAbstract, self).__init__()
        self.api_key = api_key
        self.URL = "http://api.wunderground.com/api/%s" \
            "/conditions/q/Australia/Sydney.json" % (self.api_key,)

    def parse_result_for_temperature(self, result):
        most_recent_ob = json.loads(
            result, parse_int=decimal.Decimal)["current_observation"]
        ob_datetime = datetime.datetime.fromtimestamp(
            float(most_recent_ob["local_epoch"]))
        return ob_datetime, most_recent_ob["temp_c"]


class MetwitObservationRetrieverAbstract(AbstractHTTPObservationRetriever):
    """
    http://metwit.com/developers/docs/
    """
    SOURCE = "metwit.com"


class ForecastIoObservationRetrieverAbstract(AbstractHTTPObservationRetriever):
    """
    https://developer.forecast.io/docs/v2

    "temperature": 22.53
    "time": 1364800423
    """
    SOURCE = "Forecast.io"

    def __init__(self, api_key):
        super(ForecastIoObservationRetrieverAbstract, self).__init__()
        self.api_key = api_key
        self.URL = "https://api.forecast.io/forecast/%s" \
            "/-33.86,151.21?units=si" % (self.api_key,)

    def parse_result_for_temperature(self, result):
        most_recent_ob = json.loads(
            result,
            parse_float=decimal.Decimal)["currently"]
        ob_datetime = datetime.datetime.fromtimestamp(
            float(most_recent_ob["time"]))
        return ob_datetime, most_recent_ob["temperature"]


if __name__ == "__main__":
    FORECASTIO_API_KEY = get_env_variable("FORECASTIO_API_KEY")
    WUNDERGROUND_API_KEY = get_env_variable("WUNDERGROUND_API_KEY")

    for retriever in (BOMObservationRetrieverAbstract(),
                      WundergroundObservationRetrieverAbstract(WUNDERGROUND_API_KEY),
                      ForecastIoObservationRetrieverAbstract(FORECASTIO_API_KEY)):
        d = retriever.retrieve_observation()
        d.addCallbacks(retriever.handle_observation, retriever.print_error)
        reactor.callLater(1, retriever.print_results_periodically, 5)

    reactor.run()