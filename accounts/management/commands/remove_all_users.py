from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile, ActivityLog

class Command(BaseCommand):
    help = 'Removes all users from the database including admin users'

    def handle(self, *args, **options):
        # First delete all activity logs
        ActivityLog.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Successfully deleted all activity logs'))
        
        # Then delete all user profiles
        UserProfile.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Successfully deleted all user profiles'))
        
        # Finally delete all users
        User.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Successfully deleted all users'))
        
        self.stdout.write(self.style.SUCCESS('All users have been removed from the database. You can now create a fresh admin user.')) 