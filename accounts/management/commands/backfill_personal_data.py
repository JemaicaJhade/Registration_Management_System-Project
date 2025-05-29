from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import PersonalData

class Command(BaseCommand):
    help = 'Backfill missing PersonalData objects for all existing users'

    def handle(self, *args, **options):
        for user in User.objects.all():
            PersonalData.objects.get_or_create(user=user)
            self.stdout.write(self.style.SUCCESS(f'Created PersonalData for user {user.username}')) 