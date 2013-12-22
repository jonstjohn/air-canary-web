from __future__ import print_function
from model.models import GribData
from geoalchemy2 import Geography
from sqlalchemy.exc import IntegrityError

from db import acdb

class AirNowGrib():

    OZONE = 0
    PM25 = 1
    COMBINED = 2

    OZONE_MAX = 3
    PM25_MAX = 4
    COMBINED_MAX = 5

    FORECAST_TODAY = 6
    FORECAST_TOMORROW = 7

    FILE_SUFFIX = (
        '', # Ozone
        '_pm25', # PM 2.5
        '_combined', # combined
        '-max', # Max Ozone
        '-max_pm25', # Max PM 2.5
        '-max_combined', # Max combined
        '-ForecastToday', # Forecast for today
        '-ForecastTomorrow', # Forecast for tomorrow
    )

    GRIBDATA_COLS = (
        'ozone',
        'pm25',
        'combined',
        None,
        None,
        None,
        'forecast_today',
        'forecast_tomorrow',
    )

    GRIB_DIR = '/tmp/grib2'

    def val(self, lat, lon, param, date=None, time=None):

        import subprocess
        import datetime
        import os

        if not date:
            filepath = os.path.join(self.GRIB_DIR, 'US-current{}.grib2'.format(self.FILE_SUFFIX[param]))
            #filepath = self.recent_filepath(param)
        else:
            date = datetime.date.today()
            date_part = date.strftime('%y%m%d')
            if time:
                date_part += time.strftime('%H')
            filepath = os.path.join(self.GRIB_DIR, 'US-{}{}.grib2'.format(date_part, self.FILE_SUFFIX[param]))

        output = subprocess.check_output(['/usr/local/bin/wgrib2', filepath, '-lon', lon, lat])
        parts = output.strip().split(',')
        return parts.pop().split('=')[1]

    def ozone(self, lat, lon):

        return self.val(lat, lon, self.OZONE)

    def pm25(self, lat, lon):

        return self.val(lat, lon, self.PM25)

    def combined(self, lat, lon):

        return self.val(lat, lon, self.COMBINED)

    def forecast_today(self, lat, lon):

        return self.val(lat, lon, self.FORECAST_TODAY)

    def forecast_tomorrow(self, lat, lon):

        return self.val(lat, lon, self.FORECAST_TOMORROW)

    def recent_filepath(self, param):

        import os
        import glob

        numbers = 8 if param < 6 else 6
        filepath = max(
                glob.iglob(
                    '{}/US-{}{}.grib2'.format(self.GRIB_DIR, '[0-9]' * numbers, self.FILE_SUFFIX[param])
                ), key=os.path.getctime)
        return filepath

    def csv(self, param):

        import subprocess
        import os
        filepath = os.path.join(self.GRIB_DIR, 'US-current{}.grib2'.format(self.FILE_SUFFIX[param]))
        csv_filepath = os.path.join(self.GRIB_DIR, 'US-current{}.csv'.format(self.FILE_SUFFIX[param]))
        subprocess.check_call(['/usr/local/bin/wgrib2', filepath, '-csv', csv_filepath])

    def process_csv(self, param):

        import csv
        import os

        csv_filepath = os.path.join(self.GRIB_DIR, 'US-current{}.csv'.format(self.FILE_SUFFIX[param]))

        with open(csv_filepath, 'rb') as f:

            reader = csv.reader(f)
            for row in reader:
                start, end, var, loc, lon, lat, val = row

                grib = GribData()
                grib.start = start
                grib.latitude = lat
                grib.longitude = lon
                txt = 'POINT({} {})'.format(lon, lat)
                grib.location = Geography('Point').bind_expression(txt)
                setattr(grib, self.GRIBDATA_COLS[param], val)

                try:
                    acdb.session.merge(grib)
                    acdb.session.commit()
                    print('.', end='')
                except IntegrityError as inst:
                    acdb.session.rollback()
                    print('-', end='')
                except Exception as inst:
                    acdb.session.rollback()
                    print('x', end='')
                    raise inst





                print(start, lat, lon, val)

    def grid_xy(self, lat, lon):

        """
        1:0:grid_template=0:winds(N/S):
        lat-lon grid:(1850 x 889) units 1e-06 input WE:SN output WE:SN res 48
        lat 20.000000 to 60.004999 by 0.045024
        lon 227.000000 to 310.250000 by 0.045051 #points=1644650
        """

        x_factor = (60.004999 - 20.000000) / 889
        y_factor = (310.250 - 227.000) / 1850

        #x_factor = 0.045024
        #y_factor = 0.045051

        x = int(round((lat - 20.0) / x_factor))
        if lon < 0:
            lon = 360 + lon
        print(lon)
        y = int(round((lon - 227.0) / y_factor))

        return x, y

    def grid_latlon(self, x, y):

        x_factor = (60.004999 - 20.000000) / 889
        y_factor = (227.000 - 310.25000) / 1850

        #x_factor = 0.045024
        #y_factor = 0.045051

        lat = x * x_factor + 20.0
        lon = y * y_factor + 227.0

        return lat, lon



if __name__ == '__main__':

    import datetime, os

    a = AirNowGrib()
    #a.csv(AirNowGrib.OZONE)
    #a.process_csv(AirNowGrib.OZONE)

    print()
    lat, lon = 20.0000, 227.0000
    print(lat, lon)
    x, y = a.grid_xy(lat, lon)
    print(x, y)
    print(a.grid_latlon(x, y))
    print(os.system('wgrib2 /tmp/grib2/US-current_combined.grib2 -lon {} {}'.format(lon, lat)))

    print()

    lat, lon = 60.004999, 310.250000
    print(lat, lon)
    x, y = a.grid_xy(lat, lon)
    print(x, y)
    print(a.grid_latlon(x, y))
    print(os.system('wgrib2 /tmp/grib2/US-current_combined.grib2 -lon {} {}'.format(lon, lat)))
    
    print()

    lat, lon = 40.7762, -111.8786
    print(lat, lon)
    x, y = a.grid_xy(lat, lon)
    print('grid_xy')
    print(x, y)
    print('grid_latlon')
    print(a.grid_latlon(x, y))
    print(os.system('wgrib2 /tmp/grib2/US-current_combined.grib2 -lon {} {}'.format(lon, lat)))

    """
    lat = '40.524671'
    lon = '-111.863'

    print(a.ozone(lat, lon))
    print(a.pm25(lat, lon))
    print(a.combined(lat, lon))
    """
