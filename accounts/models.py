from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
import uuid
from datetime import datetime
import random

# Create your models here.

class UserProfile(models.Model):
    USER_TYPE_CHOICES = [
        ('admin', 'Admin'),
        ('viewer', 'Viewer'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    id_number = models.CharField(max_length=20, unique=True, blank=True, null=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='viewer')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_admin(self):
        return self.user_type == 'admin'

    def save(self, *args, **kwargs):
        if not self.id_number:
            # Generate ID number based on user type and timestamp
            timestamp = datetime.now().strftime('%y%m')
            if self.user_type == 'viewer':
                # For viewers: VW-YYMM-XXXX (where XXXX is a random number)
                random_num = ''.join([str(random.randint(0, 9)) for _ in range(4)])
                self.id_number = f'VW-{timestamp}-{random_num}'
            else:
                # For admins: AD-YYMM-XXXX
                random_num = ''.join([str(random.randint(0, 9)) for _ in range(4)])
                self.id_number = f'AD-{timestamp}-{random_num}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class PersonalData(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    MARITAL_STATUS_CHOICES = [
        ('S', 'Single'),
        ('M', 'Married'),
        ('D', 'Divorced'),
        ('W', 'Widowed'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='personal_data')
    date_of_birth = models.DateField(null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    marital_status = models.CharField(max_length=20, choices=MARITAL_STATUS_CHOICES, null=True, blank=True)
    nationality = models.CharField(max_length=100, null=True, blank=True)
    emergency_contact_name = models.CharField(max_length=100, null=True, blank=True)
    emergency_contact_number = models.CharField(max_length=20, null=True, blank=True)
    blood_type = models.CharField(max_length=5, null=True, blank=True)
    medical_conditions = models.TextField(null=True, blank=True)
    allergies = models.TextField(null=True, blank=True)
    education_level = models.CharField(max_length=50, null=True, blank=True)
    employment_status = models.CharField(max_length=50, null=True, blank=True)
    hobbies = models.TextField(null=True, blank=True)
    voluntary_work = models.TextField(null=True, blank=True)
    
    # Civil Service Eligibility fields
    civil_service_eligibility = models.CharField(max_length=100, null=True, blank=True)
    eligibility_rating = models.CharField(max_length=20, null=True, blank=True)
    eligibility_date = models.DateField(null=True, blank=True)
    eligibility_place = models.CharField(max_length=100, null=True, blank=True)
    eligibility_license = models.CharField(max_length=50, null=True, blank=True)
    
    # Work Experience fields
    position_title = models.CharField(max_length=100, null=True, blank=True)
    employer_name = models.CharField(max_length=100, null=True, blank=True)
    employer_address = models.TextField(null=True, blank=True)
    employment_start_date = models.DateField(null=True, blank=True)
    employment_end_date = models.DateField(null=True, blank=True)
    monthly_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_grade = models.CharField(max_length=20, null=True, blank=True)
    job_description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Personal Data"

class ActivityLog(models.Model):
    LOGIN = 'login'
    LOGOUT = 'logout'
    ACTION_CHOICES = [
        (LOGIN, 'Login'),
        (LOGOUT, 'Logout'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.username} - {self.get_action_display()} - {self.timestamp}"

# Signal to create UserProfile and PersonalData when User is created
@receiver(post_save, sender=User)
def create_user_related_data(sender, instance, created, **kwargs):
    if created:
        # Create UserProfile if it doesn't exist
        if not hasattr(instance, 'userprofile'):
            UserProfile.objects.create(user=instance)
        
        # Create PersonalData if it doesn't exist
        if not hasattr(instance, 'personal_data'):
            PersonalData.objects.create(user=instance)

# Signal to save UserProfile and PersonalData when User is saved
@receiver(post_save, sender=User)
def save_user_related_data(sender, instance, **kwargs):
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()
    if hasattr(instance, 'personal_data'):
        instance.personal_data.save()
