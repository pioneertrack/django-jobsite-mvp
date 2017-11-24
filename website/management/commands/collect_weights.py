from django.core.management.base import BaseCommand
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta, datetime
# from statsy.models import *


class Command(BaseCommand):
    help = "Cron job command to collect documents weights used for sorting. Based on users activity."

    def handle(self, *args, **options):
        yesterday = timezone.now() - timedelta(days=1)
        start = datetime(yesterday.year, yesterday.month, yesterday.day, tzinfo=yesterday.tzinfo)
        end = start + timedelta(days=1)
        filter_args = {
            'created_at__gte': start,
            'created_at__lt': end
        }
        # query = StatsyObject \
        #     .objects \
        #     .values('user') \
        #     .filter(**filter_args) \
        #     .annotate(value=Sum('float_value')) \
        #     .order_by('user')

        self.stdout.write(self.style.SUCCESS('Weights collected'))
