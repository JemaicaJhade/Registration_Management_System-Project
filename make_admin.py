import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'registration_system.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import UserProfile

def make_user_admin():
    try:
        # Get the user
        user = User.objects.get(username='maica')
        
        # Update user permissions
        user.is_staff = True
        user.is_superuser = True
        user.save()
        
        # Update profile
        profile = UserProfile.objects.get(user=user)
        profile.is_admin = True
        profile.user_type = 'admin'
        profile.save()
        
        print("\nUser 'maica' has been updated to admin status!")
        print("Please log out and log back in to see the changes.")
        
    except User.DoesNotExist:
        print("Error: User 'maica' not found!")
    except Exception as e:
        print(f"Error updating user: {str(e)}")

if __name__ == '__main__':
    make_user_admin() 