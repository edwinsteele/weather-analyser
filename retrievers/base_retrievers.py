from twisted.internet import reactor
from twisted.web.client import getPage
from abc import ABCMeta, abstractmethod, abstractproperty
import time

__author__ = 'esteele'


class AbstractRetriever:
    __metaclass__ = ABCMeta

    def __init__(self):
        self.last_temperature_info = (None, None)

    @abstractproperty
    def source(self):
        """short description of data source"""

    @abstractproperty
    def observation_reload_delay(self):
        """time in seconds before checking for an updated observation"""

    # @abstractproperty
    def forecast_reload_delay(self):
        """time in seconds before checking for an updated forecast"""

    @abstractmethod
    def parse_observation_result_for_temperature(self, result):
        """do stuff"""

    # @abstractmethod
    def parse_forecast_result_for_temperature(self, result):
        """stuff"""

    # @abstractmethod
    def generate_observation_request_for_location(self, location):
        """takes a location object and constructs a URL that will
        retrieve an observation
        """

    def print_error(self, failure):
        print "Errback", failure

    def retrieve_observations_by_schedule(self, location):
        reactor.callLater(self.observation_reload_delay,
                          self.retrieve_observations_by_schedule,
                          location)
        print "Retrieving new observation for", self.source
        d = self.retrieve_observation(location)
        d.addCallbacks(self.handle_observation, self.print_error)

    def retrieve_observation(self, location):
        return getPage(
            self.generate_observation_request_for_location(location)
        )

    def retrieve_forecast(self, location):
        #XXX - this might not be flexible enough given some use FTP
        return getPage(
            self.generate_forecast_request_for_location(location)
        )

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
        print "Handling %s observation" % (self.source,)
        # parse
        temperature_info = self.parse_observation_result_for_temperature(result)
        # store
        self.last_temperature_info = temperature_info
