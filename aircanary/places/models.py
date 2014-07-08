from django.db import models


class Place(models.Model):

    name = None
    latitude = None
    longitude = None
    ozone = None
    pm25 = None
    combined = None
    icon = None
    summary = None
    icon_class = None
    temperature = None
    today = None
    tomorrow = None

    icon_css_map = {'clear-day': 'sun',
                      'clear-night': 'moon',
                      'rain': 'rain',
                      'snow': 'snow',
                      'sleet': 'sleet',
                      'wind': 'wind',
                      'fog': 'fog',
                      'cloudy': 'cloud',
                      'partly-cloudy-day': 'cloud sun',
                      'partly-cloudy-night': 'cloud moon'}

    def __init__(self, latitude, longitude):

        self.latitude = latitude
        self.longitude = longitude

        self._load_airnow()
        self._load_forecast()
        self._load_name()

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
        f = Forecast.Forecast(key, self.latitude, self.longitude)
        c = f.current()
        
        self.temperature = int(c['currently']['temperature'])
        self.icon = c['currently']['icon']
        self.summary = c['currently']['summary']
        self.icon_class = self._icon_to_css(self.icon)

    def _icon_to_css(self, icon):

        return self.icon_css_map[icon] if icon in self.icon_css_map else 'sun'

    def _load_name(self):
        
        from geopy import geocoders
        g = geocoders.GoogleV3()
        place, (lat, lng) = g.reverse((self.latitude, self.longitude), exactly_one=True)
        self.name = self._parse_place(place)

    def _parse_place(self, place):

        parts = place.split(',')
        if parts.pop().strip() == 'USA':
            state, zip = parts.pop().strip().split(' ')
            city = parts.pop().strip()
            return '{}, {}'.format(city, state)
        return place

    def __str__(self):

        return "{} ({},{})\nOzone: {}\nPM25: {}\nCombined: {}\nToday: {}\nTomorrow: {}\nTemperature: {}\nIcon: {}".format(self.name, self.latitude, self.longitude, self.ozone, self.pm25, self.combined, self.today, self.tomorrow, self.temperature, self.icon)
