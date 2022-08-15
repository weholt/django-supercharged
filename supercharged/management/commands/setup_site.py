from django.contrib.sites.models import Site
from django.core.management import BaseCommand


class Command(BaseCommand):
    """Django command to pause execution until db is available"""

    def handle(self, *args, **options):
        self.stdout.write("Setting up default site ...")
        one = Site.objects.all()[0]
        one.domain = input("Domain name:")
        one.name = input("Name of site:")
        one.save()
        self.stdout.write(self.style.SUCCESS("Site configured."))
