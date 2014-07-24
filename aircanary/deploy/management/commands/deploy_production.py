from django.core.management.base import BaseCommand, CommandError

from deploy.utils import deploy_production

class Command(BaseCommand):

    def handle(self, *args, **options):

        deploy_production(async=False)
