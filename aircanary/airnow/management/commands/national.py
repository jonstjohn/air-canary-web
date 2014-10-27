from django.core.management.base import BaseCommand, CommandError

import airnow
from airnow import site

class Command(BaseCommand):

    def handle(self, *args, **options):

        airnow.site.parse()
