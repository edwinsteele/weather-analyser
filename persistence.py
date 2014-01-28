from twisted.internet import reactor

__author__ = 'esteele'

import dataset


class ForecastPersister:
    """Is it really a forecast persister, or is a ob & forecast persister?

    This does blocking I/O, so isn't a good fit for twisted, but I don't really
    care. SQLAlchemy doesn't support async operation, while maintaining the ORM
    so I'm going to use it anyway and suck up the performance.
    """
    persistence_repeat_period_secs = 5

    def __init__(self, db_url):
        self.db = dataset.connect(db_url)

    def print_error(self, failure):
        print "Errback", failure

    def persist_one_forecast(self, forecast):
        table = self.db["forecast"]
        before_count = len(table)
        table.upsert(row=dict(
            source=forecast.source,
            forecast_type=forecast.forecast_type,
            start_datetime=forecast.start_datetime,
            end_datetime=forecast.end_datetime,
            issue_datetime=forecast.issue_datetime,
            temperature_min=forecast.temperature_min,
            temperature_max=forecast.temperature_max
        ), keys=[
            "source",
            "forecast_type",
            "start_datetime",
            "end_datetime",
            "issue_datetime"
        ])
        after_count = len(table)
        return after_count - before_count

    def persist_one_observation(self, observation):
        table = self.db["observation"]
        before_count = len(table)
        table.upsert(row=dict(
            source=observation.source,
            observation_datetime=observation.observation_datetime,
            temperature=observation.temperature
        ), keys=[
            "source",
            "observation_datetime"
        ])
        after_count = len(table)
        return after_count - before_count

    def persist_new_records(self, retriever):
        forecasts_inserted = 0
        observations_inserted = 0
        unpersisted_forecast_count = len(retriever.unpersisted_forecasts)
        unpersisted_observation_count = len(retriever.unpersisted_observations)
        while retriever.unpersisted_forecasts:
            forecasts_inserted += \
                self.persist_one_forecast(retriever.unpersisted_forecasts.pop())
        while retriever.unpersisted_observations:
            observations_inserted += \
                self.persist_one_observation(retriever.unpersisted_observations.pop())
        print "%s: %s of %s forecasts and " \
              "%s of %s observations actually inserted" % \
              (retriever.source,
               forecasts_inserted,
               unpersisted_forecast_count,
               observations_inserted,
               unpersisted_observation_count)

    def persist_records_forever(self, retriever):
        reactor.callLater(self.persistence_repeat_period_secs,
                          self.persist_records_forever,
                          retriever)
        self.persist_new_records(retriever)
