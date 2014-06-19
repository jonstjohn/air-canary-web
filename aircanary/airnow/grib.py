from __future__ import print_function

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

    GRIBDATA_PARAMS = (
        'ozone',
        'pm25',
        'combined',
        None,
        None,
        None,
        'today',
        'tomorrow',
    )

    GRIB_CLASS = (
        'GribOzone',
        'GribPm25',
        None,
        None,
        None,
        None,
        'GribToday',
        'GribTomorrow',
    )

    GRIB_DIR = '/tmp/grib3'

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
        """ Generate CSV for param """
        import subprocess
        import os
        filepath = os.path.join(self.GRIB_DIR, 'US-current{}.grib2'.format(self.FILE_SUFFIX[param]))
        csv_filepath = os.path.join(self.GRIB_DIR, 'US-current{}.csv'.format(self.FILE_SUFFIX[param]))
        subprocess.check_call(['/usr/local/bin/wgrib2', filepath, '-csv', csv_filepath])

    def wgrib_ij(self, lat, lon):
        """ Calculate i and j coordinates using wgrib from lat/lon """
        import subprocess
        output = subprocess.check_output(['wgrib2', '-ll2ij', lon, lat, '/tmp/grib3/US-current.grib2'])
        latpart, ijpart = output.split('->')
        j, i = ijpart.strip().strip('()').split(',')
        #print(lat, lon)
        #print(i, j)
        return int(round(float(i))), int(round(float(j)))

    def data_latlon(self, lat, lon):
        """ Get data from lat/lon
            Returns dictionary of pm25, ozone, today, tomorrow """
        import redis
        x, y = self.grid_xy(lat, lon)

        r = redis.StrictRedis(host='localhost', port=6379, db=0)

        return r.hgetall('{}:{}'.format(x,y))

    def process_csv(self, param, exists_only=False):
        """ Process CSV file for param """ 
        import csv
        import os
        import time
        import sys

        import redis

        # Setup redis
        r = redis.StrictRedis(host='localhost', port=6379, db=0)

        # CSV path
        csv_filepath = os.path.join(self.GRIB_DIR, 'US-current{}.csv'.format(self.FILE_SUFFIX[param]))

        # Parameter
        param_name = self.GRIBDATA_PARAMS[param]

        # Read CSV
        started = time.time()
        with open(csv_filepath, 'rb') as f:

            reader = csv.reader(f)

            last_x = None
            last_y = None
            rowcount = 0

            # Create redis pipeline
            pipe = r.pipeline()

            # Loop over rows
            for row in reader:

                rowcount += 1
                start, end, var, loc, lon, lat, val = row

                x, y = self.grid_xy(float(lat), float(lon))

                # Key - lat/lon translated to integers, key would be something like 1:2
                k = '{}:{}'.format(x,y)

                # Key w/ param, e.g., 1:2:pm25
                kparam = '{}:{}'.format(k, param_name)

                # If key not doing replace only or key exists, save to redis
                if not exists_only or r.exists(k):
                   
                    pipe.hmset(k, {param_name: val, '{}_start'.format(param_name): start})

                    # List for parameter history
                    #pipe.lpush(kparam, val).ltrim(kparam, 0, 71) # 3 days
                    #pipe.delete(kparam)
                   
                if rowcount % 100 == 0:
                    pipe.execute()
                    pipe = r.pipeline()

                if rowcount % 100000 == 0:
                    print()
                    print('{} rows processed in {} seconds'.format(rowcount, time.time() - started))

        pipe.execute()
        ended = time.time()

        elapsed = ended-started
        print("{} seconds".format(elapsed))

    def grid_xy(self, lat, lon):

        """
        1:0:grid_template=0:winds(N/S):
        lat-lon grid:(1850 x 889) units 1e-06 input WE:SN output WE:SN res 48
        lat 20.000000 to 60.004999 by 0.045024
        lon 227.000000 to 310.250000 by 0.045051 #points=1644650
        """

        x_factor = (60.004999 - 20.000000) / 887 # 887
        y_factor = (310.250 - 227.000) / 1851 # 1851

        #x_factor = 0.045024
        #y_factor = 0.045051

        x = int(round((lat - 20.0) / x_factor)) + 1
        if lon < 0:
            lon = 360 + lon
        #print(lon)
        y = int(round((lon - 227.0) / y_factor))

        return x, y

    def grid_latlon(self, x, y):
        """ Get grid lat lon from x, y coordinates """
        x_factor = (60.004999 - 20.000000) / 889
        y_factor = (227.000 - 310.25000) / 1850

        #x_factor = 0.045024
        #y_factor = 0.045051

        lat = x * x_factor + 20.0
        lon = y * y_factor + 227.0

        return lat, lon

def run(async=True):

    # Download
    from airnow.utils import Ftp
    f = Ftp()
    f.grib2_download()
    f.close

    # Convert to csv and process
    from airnow.tasks import grib_process_csv

    a = AirNowGrib()
    #grib_process_csv.delay(AirNowGrib.PM25)

    for param in (AirNowGrib.PM25, AirNowGrib.OZONE, AirNowGrib.FORECAST_TODAY, AirNowGrib.FORECAST_TOMORROW):
        a.csv(param)
        if async:
            grib_process_csv.delay(param) # run async
        else:
            a.process_csv(param)

if __name__ == '__main__':

    import datetime, os

    a = AirNowGrib()
    #a.csv(AirNowGrib.OZONE)
    #a.process_csv(AirNowGrib.OZONE)

    print()
    lat, lon = 40.7500, -111.8833
    print(lat, lon)
    x, y = a.grid_xy(lat, lon)
    print(x, y)
    print(a.grid_latlon(x, y))
    print(os.system('wgrib2 /tmp/grib3/US-current_combined.grib2 -lon {} {}'.format(lon, lat)))
    print(os.system('wgrib2 /tmp/grib3/US-current-ForecastToday.grib2 -lon {} {}'.format(lon, lat)))
    print(os.system('wgrib2 /tmp/grib3/US-current-ForecastTomorrow.grib2 -lon {} {}'.format(lon, lat)))

    print()
    lat, lon = 20.0000, 227.0000
    print(lat, lon)
    x, y = a.grid_xy(lat, lon)
    print(x, y)
    print(a.grid_latlon(x, y))
    print(os.system('wgrib2 /tmp/grib3/US-current_combined.grib2 -lon {} {}'.format(lon, lat)))

    print()

    lat, lon = 60.004999, 310.250000
    print(lat, lon)
    x, y = a.grid_xy(lat, lon)
    print(x, y)
    print(a.grid_latlon(x, y))
    print(os.system('wgrib2 /tmp/grib3/US-current_combined.grib2 -lon {} {}'.format(lon, lat)))
    
    print()

    lat, lon = 40.7762, -111.8786
    print(lat, lon)
    x, y = a.grid_xy(lat, lon)
    print('grid_xy')
    print(x, y)
    print('grid_latlon')
    print(a.grid_latlon(x, y))
    print(os.system('wgrib2 /tmp/grib3/US-current_combined.grib2 -lon {} {}'.format(lon, lat)))

    """
    lat = '40.524671'
    lon = '-111.863'

    print(a.ozone(lat, lon))
    print(a.pm25(lat, lon))
    print(a.combined(lat, lon))
    """
