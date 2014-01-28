from __future__ import print_function
from twisted.internet import reactor
from twisted.web.client import getPage
from abc import ABCMeta, abstractmethod, abstractproperty

__author__ = 'esteele'


class AbstractRetriever:
    __metaclass__ = ABCMeta

    def __init__(self):
        self.unpersisted_observations = []
        self.unpersisted_forecasts = []

    @abstractproperty
    def source(self):
        """short description of data source"""

    @abstractproperty
    def observation_reload_delay(self):
        """time in seconds before checking for an updated observation"""

    @abstractproperty
    def forecast_reload_delay(self):
        """time in seconds before checking for an updated forecast"""

    @abstractmethod
    def parse_observation_response(self, result):
        """do stuff"""

    @abstractmethod
    def parse_forecast_response(self, result):
        """stuff"""

    @abstractmethod
    def generate_observation_request_for_location(self, location):
        """takes a location object and constructs a URL that will
        retrieve an observation
        """

    @abstractmethod
    def generate_forecast_request_for_location(self, location):
        """takes a location object and constructs a URL that will
        retrieve a forecast
        """

    def print_error(self, failure):
        print("Errback", failure)

    def retrieve_observations_by_schedule(self, location):
        reactor.callLater(self.observation_reload_delay,
                          self.retrieve_observations_by_schedule,
                          location)
        print("%s: Retrieving new observation" % (self.source,))
        d = self.retrieve_observation(location)
        d.addCallbacks(self.handle_observation, self.print_error)

    def retrieve_observation(self, location):
        return getPage(
            self.generate_observation_request_for_location(location)
        )

    def retrieve_forecasts_by_schedule(self, location):
        reactor.callLater(self.forecast_reload_delay,
                          self.retrieve_forecasts_by_schedule,
                          location)
        print("%s: Retrieving new forecast" % (self.source,))
        d = self.retrieve_forecast(location)
        d.addCallbacks(self.handle_forecast, self.print_error)

    def retrieve_forecast(self, location):
        return getPage(
            self.generate_forecast_request_for_location(location)
        )

    def print_results_periodically(self, period_seconds):
        reactor.callLater(period_seconds,
                          self.print_results_periodically,
                          period_seconds)
        [o.print_summary() for o in self.unpersisted_observations]
        [f.print_summary() for f in self.unpersisted_forecasts]
        # print "Delayed calls:"
        # pprint.pprint([r.func for r in reactor.getDelayedCalls()])

    def handle_observation(self, response):
        print("%s: Handling observation" % (self.source,), end='')
        # parse
        ob = self.parse_observation_response(response)
        # store
        self.unpersisted_observations.append(ob)
        [o.print_summary() for o in self.unpersisted_observations]

    def handle_forecast(self, response):
        print("%s: Handling forecast" % (self.source,), end='')
        # parse
        forecasts = self.parse_forecast_response(response)
        # store
        self.unpersisted_forecasts.extend(forecasts)
        [f.print_summary() for f in self.unpersisted_forecasts]
