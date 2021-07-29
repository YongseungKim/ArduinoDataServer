from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from optparse import make_option
from random import randint

from arduino_server import models


class Command(BaseCommand):
    args = '--dummy'
    help = 'Insert a bunch of test data history for all available meters. Useful for development. ' \
           'You should probably run ./manage.py reset djangodataserver before this.'  # @ReservedAssignment
    # option_list = BaseCommand.option_list + (
    #     make_option('--entries', '-e', action='store', dest='entries',
    #                 default="100",
    #                 help='Number of entries to generate for each meter (default: 100)'),
    #     make_option('--hourly', action='store_true', dest='hourly',
    #                 default=False,
    #                 help='Number of entries to generate for each meter (default: 100)'),
    #     make_option('--daily', action='store_true', dest='daily',
    #                 default=False,
    #                 help='Number of entries to generate for each meter (default: 100)'),
    # )

    def add_arguments(self, parser):
        parser.add_argument(
            '--entries',
            type=int,
            dest='entries',
            action='store',
            default=100,
            help='Number of entries to generate for each meter (default: 100)')

        parser.add_argument(
            '--hourly',
            type=bool,
            dest='hourly',
            action='store_true',
            default=False,
            help='Specify a file to put our process ID in (for daemon mode)')

        parser.add_argument(
            '--daily',
            type=bool,
            dest='daily',
            action='store_true',
            default=False,
            help='Specify the ip address to listen to.')

    def handle(self, *args, **options):

        entries = int(options["entries"])
        hourly = options["hourly"]
        daily = options["daily"]

        if not (hourly or daily): hourly = True

        min_insert = 0
        max_insert = 100

        for meter in models.Meter.objects.all():
            if daily:
                current_date = datetime.now() - timedelta(days=entries)
                for __ in range(entries):
                    point = randint(min_insert, max_insert)
                    data_entry = models.MeterData(data_point=point,
                                                  created=current_date,
                                                  meter=meter)
                    data_entry.save()
                    current_date = current_date + timedelta(days=1)

            if hourly:
                current_date = datetime.now() - timedelta(hours=entries)
                for __ in range(entries):
                    point = randint(min_insert, max_insert)
                    data_entry = models.MeterData(data_point=point,
                                                  created=current_date,
                                                  meter=meter)
                    data_entry.save()
                    current_date = current_date + timedelta(hours=1)
