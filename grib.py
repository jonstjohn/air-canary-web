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

if __name__ == '__main__':

    import datetime
    a = AirNowGrib()
    #a.csv(AirNowGrib.OZONE)
    a.process_csv(AirNowGrib.OZONE)
    """
    lat = '40.524671'
    lon = '-111.863'

    print(a.ozone(lat, lon))
    print(a.pm25(lat, lon))
    print(a.combined(lat, lon))
    """
