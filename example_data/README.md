forecast_io_observation_and_forecast.json obtained from:
curl https://api.forecast.io/forecast/<API_KEY>/-33.86,151.21?units=si | python -mjson.tool

bom_observation.json obtained from:
http://www.bom.gov.au/fwo/IDN60901/IDN60901.94768.json

wunderground_observation.json obtained from:
http://api.wunderground.com/api/<API_KEY>/conditions/q/Australia/Sydney.json
http://api.wunderground.com/api/<API_KEY>/conditions/q/Australia/Sydney%20Regional%20Office.json
