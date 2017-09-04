from django.core.management.base import BaseCommand
from website.profile import Profile, Founder
from django.db import transaction
from django.template.loader import render_to_string


class Command(BaseCommand):
    help = "Send emails for users and startup owners with incomplete profiles"

    def handle(self, *args, **options):
        with transaction.atomic():
            result = Profile.objects.filter(is_filled=False)
            for item in result:
                message =  render_to_string('email/user_profile_incomplete.txt', {'profile': item})
                item.user.email_user('You personal profile is incomplete', message, 'noreply@bearfounders.com')
        self.stdout.write(self.style.SUCCESS('"%s" Emails in queue for User profiles' % result.count()))
        with transaction.atomic():
            result = Founder.objects.filter(is_filled=False)
            for item in result:
                message =  render_to_string('email/startup_profile_incomplete.txt', {'profile': item})
                item.user.email_user('You startup profile is incomplete', message, 'noreply@bearfounders.com')

        self.stdout.write(self.style.SUCCESS('"%s" Emails in queue for Startup profiles' % result.count()))
