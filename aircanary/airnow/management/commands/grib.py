from django.core.management.base import BaseCommand, CommandError

import airnow

class Command(BaseCommand):

    def handle(self, *args, **options):

        airnow.grib.run(async=False)
