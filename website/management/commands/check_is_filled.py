from django.core.management.base import BaseCommand
from website.profile import Profile, Founder
from django.db import transaction

class Command(BaseCommand):
    help = "Set is_filled flag on Profiles and Founders."

    def handle(self, *args, **options):
        self.stdout.write('Check Founders')
        with transaction.atomic():
            result = Founder.objects.all()
            for item in result:
                item.check_is_filled(save=False)
                if not item.is_filled:
                    self.stdout.write(self.style.SUCCESS('id: {} email: {}'.format(item.user.id, item.user.email)))
        self.stdout.write(self.style.SUCCESS('Checked "{}" Founder Profiles'.format(result.count())))
        self.stdout.write('-')
        self.stdout.write('Check Profiles')
        with transaction.atomic():
            result = Profile.objects.all()
            for item in result:
                item.check_is_filled(save=False)
                if not item.is_filled:
                    self.stdout.write(self.style.SUCCESS('id: {} email: {}'.format(item.user.id, item.user.email)))
        self.stdout.write(self.style.SUCCESS('Checked "{}" User Profiles'.format(result.count())))
