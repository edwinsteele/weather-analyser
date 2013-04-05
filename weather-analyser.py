from twisted.internet import reactor
import os
import location_adapter
from retrievers.bom_retriever import BOMRetriever
from retrievers.wunderground_retriever import WundergroundRetriever
from retrievers.forecastio_retriever import ForecastIoRetriever

__author__ = 'esteele'


def get_env_variable(var_name):
    """ Get the environment variable or return exception """
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = "Set the %s env variable" % var_name
        raise RuntimeError(error_msg)


if __name__ == "__main__":
    FORECASTIO_API_KEY = get_env_variable("FORECASTIO_API_KEY")
    WUNDERGROUND_API_KEY = get_env_variable("WUNDERGROUND_API_KEY")

    location = location_adapter.Sydney()

    for retriever in (BOMRetriever(),
                      WundergroundRetriever(WUNDERGROUND_API_KEY),
                      ForecastIoRetriever(FORECASTIO_API_KEY)):
        retriever.retrieve_observations_by_schedule(location)
        reactor.callLater(1, retriever.print_results_periodically, 10)

    reactor.run()
