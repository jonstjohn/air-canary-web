from django.db import models

class Aqi(models.Model):
    """Air Quality Index from airnow
    """

    # Integer value
    value = None

    # Name, e.g., 'Good', 'Moderate'
    label = None
    css = None

    ranges = [
        {'low': 0, 'high': 50, 'label': 'Good', 'css': 'aqi-green'},
        {'low': 50, 'high': 100, 'label': 'Moderate', 'css': 'aqi-yellow'},
        {'low': 100, 'high': 150, 'label': 'Unhealthy for Sensitive Groups', 'css': 'aqi-orange'},
        {'low': 150, 'high': 200, 'label': 'Unhealthy', 'css': 'aqi-red'},
        {'low': 200, 'high': 250, 'label': 'Hazardous', 'css': 'aqi-purple'},
        {'low': 250, 'high': 1000, 'label': 'Extremely Hazardous', 'css': 'aqi-maroon'}
    ]

    def __init__(self, value):
        """Constructor with an integer value
        """

        if not value:
            self.value = None
            self.css = 'aqi-none'
            self.label = 'n/a'

        else:

            self.value = int(value)

            for r in self.ranges:
                if self.value <= r['high']:
                    self.label = r['label']
                    self.css = r['css']
                    break

    def __str__(self):

        return "{} - {} - {}".format(self.value, self.label, self.css)

