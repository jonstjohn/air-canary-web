
class Forecast():

    apikey = None
    latitude = None
    longitude = None

    url = 'https://api.forecast.io/forecast'

    def __init__(self, apikey, latitude, longitude):

        self.apikey = apikey
        self.latitude = latitude
        self.longitude = longitude

    def current(self):

        import requests

        # https://api.forecast.io/forecast/30d052b50af0d59a4f2224d57dd0ce84/37.8267,-122.423?exclude=hourly,daily,flags,minutely
        url = '{}/{}/{},{}?exclude=hourly,daily,flags,minutely'.format(self.url, self.apikey, self.latitude, self.longitude)

        r = requests.get(url)
        return r.json()

