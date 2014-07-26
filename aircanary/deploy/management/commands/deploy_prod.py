from django.core.management.base import BaseCommand, CommandError

from deploy.utils import deploy_prod

class Command(BaseCommand):

    def handle(self, *args, **options):

        deploy_prod()
