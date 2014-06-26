from django.db import models

class Place(models.Model):

    name = None
    latitude = None
    longitude = None
    ozone = None
    pm25 = None
    combined = None
    icon = None
    temperature = None
    today = None
    tomorrow = None

    def __init__(self, latitude, longitude):

        self.latitude = latitude
        self.longitude = longitude

        self._load_airnow()
        self._load_forecast()

    def _load_airnow(self):

        # Load ozone, pm25
        from airnow.grib import AirNowGrib
        a = AirNowGrib()
        r = a.data_latlon(self.latitude, self.longitude)
        if 'ozone' in r:
            self.combined = r['ozone'] if float(r['ozone']) > float(r['pm25']) else r['pm25']
        self.pm25 = r['pm25']
        self.ozone = r['ozone']
        self.today = r['today']
        self.tomorrow = r['tomorrow']

    def _load_forecast(self):

        import os
        from places import Forecast
        key = os.environ['FORECAST_IO_KEY']
        f = Forecast.Forecast(key, '37.8267', '-122.423')
        c = f.current()

        self.temperature = c['currently']['temperature']
        self.icon = c['currently']['icon']

    def __str__(self):

        return "{} ({},{})\nOzone: {}\nPM25: {}\nCombined: {}\nToday: {}\nTomorrow: {}\nTemperature: {}\nIcon: {}".format(self.name, self.latitude, self.longitude, self.ozone, self.pm25, self.combined, self.today, self.tomorrow, self.temperature, self.icon)
