from django.db import models


class Place(models.Model):
    """A place, identified by latitude and longitude, includes
    a name, air quality data and current weather conditions
    """
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
    current = None

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
        """Loads airnow data, forecast and place name
        """
        self.latitude = latitude
        self.longitude = longitude

        self._load_airnow()
        self._load_forecast()
        self._load_name()

    def _load_airnow(self):
        """Load air quality data
        """
        # Load ozone, pm25
        import airnow
        from airnow.grib import AirNowGrib

        combined = None
        pm25 = None
        ozone = None
        today = None
        tomorrow = None

        a = AirNowGrib()
        r = a.data_latlon(self.latitude, self.longitude)

        if r:
            if 'pm25' in r:
                pm25 = r['pm25']
                combined = pm25

            if 'ozone' in r:
                ozone = r['ozone']
                if float(ozone) > float(pm25):
                    combined = ozone

            if 'today' in r:
                today = r['today']

            if 'tomorrow' in r:
                tomorrow = r['tomorrow']

        self.combined = airnow.models.Aqi(combined)
        self.pm25 = airnow.models.Aqi(pm25)
        self.ozone = airnow.models.Aqi(ozone)
        self.today = airnow.models.Aqi(today)
        self.tomorrow = airnow.models.Aqi(tomorrow)

    def _load_forecast(self):
        """Load forecast
        """
        import os
        from places import Forecast
        key = os.environ['FORECAST_IO_KEY']
        f = Forecast.Forecast(key, self.latitude, self.longitude)
        c = f.current()
        
        self.temperature = int(c['currently']['temperature'])
        self.icon = c['currently']['icon']
        self.summary = c['currently']['summary']
        self.icon_class = self._icon2css(self.icon)

    def _icon2css(self, icon):
        """Convert forecast icon to css class
        """
        return self.icon_css_map[icon] if icon in self.icon_css_map else 'sun'

    def _aqi2css(self):
        """Convert AQI to css class
        """
        from airnow import models

        for d in self.aqi_ranges:
            pass # TODO

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

    @staticmethod
    def from_name(name):
        """ Get a place instance from name
        Geeocdes the place """
        from geopy import geocoders
        g = geocoders.GoogleV3()
        place, (lat, lng) = g.geocode(name)
        return Place(lat, lng)

    def __str__(self):

        return "\n".join(
                (
                    self.name,
                    "Latitude: {}".format(self.latitude),
                    "Longitude: {}".format(self.longitude),
                    "Ozone: {}".format(self.ozone),
                    "PM2.5: {}".format(self.pm25),
                    "Combined: {}".format(self.combined),
                    "Today: {}".format(self.today),
                    "Tomorrow: {}".format(self.tomorrow),
                    "Temperature: {}".format(self.temperature),
                    "Icon: {}".format(self.icon)
                )
            )
