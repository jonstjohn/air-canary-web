
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

if __name__ == '__main__':

    import datetime
    a = AirNowGrib()
    lat = '40.524671'
    lon = '-111.863'

    print(a.ozone(lat, lon))
    print(a.pm25(lat, lon))
    print(a.combined(lat, lon))
