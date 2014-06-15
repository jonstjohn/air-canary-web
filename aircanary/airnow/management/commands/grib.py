from django.core.management.base import BaseCommand, CommandError

from airnow.grib import AirNowGrib
import airnow

class Command(BaseCommand):

    def handle(self, *args, **options):

        airnow.grib.run()
