import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'registration_system.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import UserProfile

def fix_admin_user():
    try:
        # Delete existing maica user if exists
        User.objects.filter(username='maica').delete()
        
        # Create new admin user
        user = User.objects.create_user(
            username='maica',
            email='maica@example.com',
            password='maica123',
            first_name='Maica',
            last_name='Admin',
            is_staff=True,
            is_superuser=True
        )
        
        # Create admin profile
        profile = UserProfile.objects.create(
            user=user,
            is_admin=True
        )
        
        print("\nAdmin user has been reset and created with proper permissions!")
        print("Username: maica")
        print("Password: maica123")
        print("\nPlease try logging in again!")
        
    except Exception as e:
        print(f"Error fixing admin user: {str(e)}")

if __name__ == '__main__':
    fix_admin_user() 