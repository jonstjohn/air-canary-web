from django.core.management.base import BaseCommand, CommandError

from airnow.grib import AirNowGrib

class Command(BaseCommand):

    def handle(self, *args, **options):

        # Download
        from airnow.utils import Ftp
        f = Ftp()
        f.grib2_download()
        f.close

        # Convert to csv and process
        a = AirNowGrib()
        for param in (AirNowGrib.PM25, AirNowGrib.OZONE):
            a.csv(param)
            a.process_csv(param)

        for param in (AirNowGrib.FORECAST_TODAY, AirNowGrib.FORECAST_TOMORROW):
            a.csv(param)
            a.process_csv(param, True)
        self.stdout.write('Grib!')
