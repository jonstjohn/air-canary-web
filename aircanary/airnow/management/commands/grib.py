from django.core.management.base import BaseCommand, CommandError

from airnow import grib

class Command(BaseCommand):

    def handle(self, *args, **options):

        grib.run(async=False)
