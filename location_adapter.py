__author__ = 'esteele'


class LocationAdapter(object):
    pass


class Sydney(LocationAdapter):
    LAT = -33.86  # As obtained from forecast.io
    LON = 151.21  # As obtained from forecast.io
    BOM_STATE = "N"
    BOM_STATION = 94768
    WUNDERGROUND_MAJOR_LOC = "Australia"
    #WUNDERGROUND_MINOR_LOC = "Sydney"
    WUNDERGROUND_MINOR_LOC = "Sydney%20Regional%20Office"
