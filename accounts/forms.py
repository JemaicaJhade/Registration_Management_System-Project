from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, PersonalData

class UserRegistrationForm(UserCreationForm):
    # Account Information
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone_number = forms.CharField(max_length=15, required=True)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'first_name', 'last_name',
                 'phone_number', 'address')

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken. Please choose a different one.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already registered. Please use a different one.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            
        return user

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field_name == 'address':
                field.widget.attrs['placeholder'] = 'Enter your complete address'
            elif field_name == 'username':
                field.widget.attrs['placeholder'] = 'Choose a unique username'
            elif field_name == 'email':
                field.widget.attrs['placeholder'] = 'Enter your email address'
            elif field_name == 'phone_number':
                field.widget.attrs['placeholder'] = 'Enter your phone number'

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'address', 'salary']
        widgets = {
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'salary': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

class PersonalDataForm(forms.ModelForm):
    class Meta:
        model = PersonalData
        fields = [
            'date_of_birth', 'age', 'email', 'gender', 'marital_status', 'nationality',
            'emergency_contact_name', 'emergency_contact_number', 'blood_type',
            'medical_conditions', 'allergies', 'education_level',
            'employment_status', 'hobbies', 'voluntary_work',
            'civil_service_eligibility', 'eligibility_rating', 'eligibility_date',
            'eligibility_place', 'eligibility_license',
            'position_title', 'employer_name', 'employer_address',
            'employment_start_date', 'employment_end_date', 'monthly_salary',
            'salary_grade', 'job_description'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '150'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'eligibility_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'employment_start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'employment_end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'medical_conditions': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'allergies': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'hobbies': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'voluntary_work': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'employer_address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'job_description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        } 