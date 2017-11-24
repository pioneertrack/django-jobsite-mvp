from django.core.management.base import BaseCommand
from website.models import MyUser


class Command(BaseCommand):
    help = "Set last activity on last login time."

    def handle(self, *args, **options):
        res = MyUser.objects.all()
        for rec in res:
            rec.last_activity = rec.last_login
            rec.save()

        self.stdout.write(self.style.SUCCESS('Updated "{}" Users'.format(res.count())))
