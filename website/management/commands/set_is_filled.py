from django.core.management.base import BaseCommand
from website.profile import Profile, Founder
from django.db import transaction

class Command(BaseCommand):
    help = "Set is_filled flag on Profiles and Founders."

    def handle(self, *args, **options):
        with transaction.atomic():
            result = Founder.objects.all()
            for item in result:
                item.check_is_filled()
        self.stdout.write(self.style.SUCCESS('Updated "{}" Founder Profiles'.format(result.count())))
        with transaction.atomic():
            result = Profile.objects.all()
            for item in result:
                item.check_is_filled()
        self.stdout.write(self.style.SUCCESS('Updated "{}" User Profiles'.format(result.count())))
