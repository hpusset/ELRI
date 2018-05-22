from django.core.management import BaseCommand
from metashare.report_utils.pivot_tables import create_pivot_report


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write("Creating CEF Digital pivot report\n")
        self.stdout.write(str(create_pivot_report))
