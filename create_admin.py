import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'registration_system.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import UserProfile

def create_admin_user():
    try:
        # Check if user already exists
        if User.objects.filter(username='maica').exists():
            user = User.objects.get(username='maica')
            print("User 'maica' already exists. Updating admin status...")
        else:
            # Create the admin user
            user = User.objects.create_user(
                username='maica',
                email='maica@example.com',
                password='maica123',  # You should change this password
                first_name='Maica',
                last_name='Admin',
                is_staff=True,
                is_superuser=True
            )
            print("Created new admin user 'maica'")

        # Ensure the user is an admin
        user.is_staff = True
        user.is_superuser = True
        user.save()

        # Create and set up the admin profile
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.is_admin = True
        profile.save()
        
        print("\nAdmin user 'maica' is now set up with admin privileges!")
        print("Username: maica")
        print("Password: maica123")
        print("\nPlease change the password after first login!")
        
    except Exception as e:
        print(f"Error creating admin user: {str(e)}")

if __name__ == '__main__':
    create_admin_user() 