from twisted.internet import reactor
from twisted.web.client import getPage
from abc import ABCMeta, abstractmethod, abstractproperty
import datetime
import decimal
import json
import os
import pprint
import time
import location_adapter

__author__ = 'esteele'


def get_env_variable(var_name):
    """ Get the environment variable or return exception """
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = "Set the %s env variable" % var_name
        raise RuntimeError(error_msg)


class AbstractHTTPObservationRetriever:
    __metaclass__ = ABCMeta

    def __init__(self):
        self.last_temperature_info = (None, None)

    @abstractproperty
    def source(self):
        """short description of data source"""

    @abstractproperty
    def observation_reload_delay(self):
        """time in seconds before checking for an updated observation"""

    @abstractmethod
    def parse_result_for_temperature(self, result):
        """do stuff"""

    @abstractmethod
    def generate_observation_request_for_location(self, location):
        """takes a location object and constructs a URL that will
        retrieve an observation
        """

    def print_error(self, result):
        print "Errback", result

    def retrieve_observations_by_schedule(self, location):
        reactor.callLater(self.observation_reload_delay,
                          self.retrieve_observations_by_schedule,
                          location)
        print "Retrieving new ob for", self.source
        d = self.retrieve_observation(location)
        d.addCallbacks(self.handle_observation, self.print_error)

    def retrieve_observation(self, location):
        return getPage(
            self.generate_observation_request_for_location(location))

    def print_results_periodically(self, period_seconds):
        reactor.callLater(period_seconds,
                          self.print_results_periodically,
                          period_seconds)
        print "%s: %s last result: time %s, air temp %s" % (
            time.ctime(),
            self.source,
            self.last_temperature_info[0],
            self.last_temperature_info[1])
        # print "Delayed calls:"
        # pprint.pprint([r.func for r in reactor.getDelayedCalls()])

    def handle_observation(self, result):
        print "Handling ob for ", self.source
        # parse
        temperature_info = self.parse_result_for_temperature(result)
        # store
        self.last_temperature_info = temperature_info


class BOMObservationRetriever(AbstractHTTPObservationRetriever):
    """
    http://www.bom.gov.au/products/IDN60901/IDN60901.94768.shtml#other_formats

    local_date_time_full": "20130401180000"
    air_temp": 21.8

    URL format: IDQ60901
    """
    def __init__(self):
        super(BOMObservationRetriever, self).__init__()

    @property
    def source(self):
        return "BOM"

    @property
    def observation_reload_delay(self):
        return 30

    def generate_observation_request_for_location(self, location):
        return "http://www.bom.gov.au/fwo/ID%s60901/IDN60901.%s.json" % (
            location.BOM_STATE,
            location.BOM_STATION
        )

    def parse_result_for_temperature(self, result):
        most_recent_ob = json.loads(
            result, parse_float=decimal.Decimal)["observations"]["data"][0]
        ob_datetime = datetime.datetime.strptime(
            most_recent_ob["local_date_time_full"],
            "%Y%m%d%H%M%S")
        return ob_datetime, most_recent_ob["air_temp"]


class WundergroundObservationRetriever(AbstractHTTPObservationRetriever):
    """
    http://www.wunderground.com/weather/api/d/docs

    "local_epoch":"1364800751"
    "temp_c":22
    """
    def __init__(self, api_key):
        super(WundergroundObservationRetriever, self).__init__()
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

    def parse_result_for_temperature(self, result):
        most_recent_ob = json.loads(
            result, parse_int=decimal.Decimal)["current_observation"]
        ob_datetime = datetime.datetime.fromtimestamp(
            float(most_recent_ob["local_epoch"]))
        return ob_datetime, most_recent_ob["temp_c"]


class ForecastIoObservationRetriever(AbstractHTTPObservationRetriever):
    """
    https://developer.forecast.io/docs/v2

    "temperature": 22.53
    "time": 1364800423
    """
    def __init__(self, api_key):
        super(ForecastIoObservationRetriever, self).__init__()
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

    def parse_result_for_temperature(self, result):
        most_recent_ob = json.loads(
            result,
            parse_float=decimal.Decimal)["currently"]
        ob_datetime = datetime.datetime.fromtimestamp(
            float(most_recent_ob["time"]))
        return ob_datetime, most_recent_ob["temperature"]


class MetwitObservationRetriever(AbstractHTTPObservationRetriever):
    """
    http://metwit.com/developers/docs/
    """
    @property
    def source(self):
        return "metwit"


if __name__ == "__main__":
    FORECASTIO_API_KEY = get_env_variable("FORECASTIO_API_KEY")
    WUNDERGROUND_API_KEY = get_env_variable("WUNDERGROUND_API_KEY")

    location = location_adapter.Sydney()

    for retriever in (BOMObservationRetriever(),
                      WundergroundObservationRetriever(WUNDERGROUND_API_KEY),
                      ForecastIoObservationRetriever(FORECASTIO_API_KEY)):
        retriever.retrieve_observations_by_schedule(location)
        reactor.callLater(1, retriever.print_results_periodically, 10)

    reactor.run()