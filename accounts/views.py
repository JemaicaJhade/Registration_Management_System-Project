from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import ActivityLog, UserProfile, PersonalData
from .forms import UserRegistrationForm, UserProfileForm, UserEditForm, PersonalDataForm
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.core.paginator import Paginator
from django.db.models import Q

def is_admin(user):
    return user.userprofile.is_admin

# Create your views here.

# Registration view
def register_view(request):
    if request.user.is_authenticated:
        return redirect('profile')
        
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                # Save the user first
                user = form.save()
                
                # Update the profile with additional data
                user.userprofile.phone_number = form.cleaned_data['phone_number']
                user.userprofile.address = form.cleaned_data['address']
                user.userprofile.save()
                
                login(request, user)
                messages.success(request, 'Registration successful! Welcome to the system.')
                return redirect('profile')
            except Exception as e:
                messages.error(request, f'Error creating account: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{error}')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

# Login view
@ensure_csrf_cookie
def login_view(request):
    if request.user.is_authenticated:
        return redirect('profile')
        
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # Create activity log
            ActivityLog.objects.create(
                user=user,
                action=ActivityLog.LOGIN,
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, f'Welcome back, {user.username}!')
            
            # Redirect based on user type
            if user.userprofile.is_admin:
                return redirect('admin_dashboard')
            return redirect('profile')
    else:
        form = AuthenticationForm()
    
    # Get the next URL from GET parameters
    next_url = request.GET.get('next')
    
    return render(request, 'accounts/login.html', {
        'form': form,
        'next': next_url
    })

# Logout view
@login_required
def logout_view(request):
    ActivityLog.objects.create(user=request.user, action=ActivityLog.LOGOUT)
    logout(request)
    return redirect('login')

# Activity log view
@login_required
def activity_log_view(request):
    if request.user.userprofile.is_admin:
        logs = ActivityLog.objects.select_related('user').order_by('-timestamp')
    else:
        logs = ActivityLog.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, 'accounts/activity_log.html', {'logs': logs})

# Home view
def root(request):
    if request.user.is_authenticated:
        if request.user.userprofile.is_admin:
            return redirect('admin_dashboard')
        return redirect('profile')
    return render(request, 'accounts/root.html')

# Profile view
@login_required
def profile(request):
    # Get user's activity logs
    activity_logs = ActivityLog.objects.filter(user=request.user).order_by('-timestamp')[:5]
    
    # Get statistics for admin users
    if request.user.userprofile.user_type == 'admin':
        total_users = User.objects.count()
        admin_users = UserProfile.objects.filter(user_type='admin').count()
        viewer_users = UserProfile.objects.filter(user_type='viewer').count()
        active_today = ActivityLog.objects.filter(
            timestamp__gte=timezone.now() - timedelta(days=1)
        ).values('user').distinct().count()
    else:
        total_users = None
        admin_users = None
        viewer_users = None
        active_today = None

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user.userprofile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user.userprofile)

    context = {
        'activity_logs': activity_logs,
        'total_users': total_users,
        'admin_users': admin_users,
        'viewer_users': viewer_users,
        'active_today': active_today,
        'form': form,
    }
    return render(request, 'accounts/profile.html', context)

# Admin dashboard view
@login_required
def admin_dashboard(request):
    if not request.user.userprofile.user_type == 'admin':
        messages.error(request, 'You do not have permission to access the admin dashboard.')
        return redirect('profile')
        
    # Get user statistics
    total_users = User.objects.count()
    total_viewers = UserProfile.objects.filter(user_type='viewer').count()
    total_admins = UserProfile.objects.filter(user_type='admin').count()
    
    # Get recent activity
    recent_activity = ActivityLog.objects.select_related('user').order_by('-timestamp')[:10]
    
    # Get recent registrations
    recent_registrations = User.objects.select_related('userprofile').order_by('-date_joined')[:5]
    
    context = {
        'total_users': total_users,
        'total_viewers': total_viewers,
        'total_admins': total_admins,
        'recent_activity': recent_activity,
        'recent_registrations': recent_registrations,
    }
    
    return render(request, 'accounts/admin_dashboard.html', context)

# User management views (admin only)
@login_required
@user_passes_test(is_admin)
def user_list(request):
    users = User.objects.select_related('userprofile').all()
    return render(request, 'accounts/user_list.html', {'users': users})

@login_required
@user_passes_test(is_admin)
def user_detail(request, user_id):
    user_obj = get_object_or_404(User, id=user_id)
    
    # Check if the user has permission to view this profile
    if not request.user.userprofile.is_admin and request.user != user_obj:
        messages.error(request, 'You do not have permission to view this profile.')
        return redirect('profile')
    
    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=user_obj)
        profile_form = UserProfileForm(request.POST, instance=user_obj.userprofile)
        personal_data_form = PersonalDataForm(request.POST, instance=user_obj.personal_data)
        
        if user_form.is_valid() and profile_form.is_valid() and personal_data_form.is_valid():
            user_form.save()
            profile_form.save()
            personal_data_form.save()
            messages.success(request, 'User information updated successfully.')
            return redirect('user_detail', user_id=user_id)
    else:
        user_form = UserEditForm(instance=user_obj)
        profile_form = UserProfileForm(instance=user_obj.userprofile)
        personal_data_form = PersonalDataForm(instance=user_obj.personal_data)
    
    # Get user's activity logs
    activity_logs = ActivityLog.objects.filter(user=user_obj).order_by('-timestamp')[:10]
    
    context = {
        'user_obj': user_obj,
        'user_form': user_form,
        'profile_form': profile_form,
        'personal_data_form': personal_data_form,
        'activity_logs': activity_logs,
        'is_admin': request.user.userprofile.is_admin,
    }
    return render(request, 'accounts/user_detail.html', context)

@login_required
def user_edit(request, user_id):
    if not request.user.userprofile.is_admin:
        messages.error(request, 'You do not have permission to edit users.')
        return redirect('user_list')
    
    user_to_edit = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=user_to_edit)
        profile_form = UserProfileForm(request.POST, instance=user_to_edit.userprofile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'User updated successfully.')
            return redirect('user_list')
    else:
        user_form = UserEditForm(instance=user_to_edit)
        profile_form = UserProfileForm(instance=user_to_edit.userprofile)
    
    return render(request, 'accounts/user_edit.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'user_to_edit': user_to_edit
    })

@login_required
def edit_personal_data(request, user_id=None):
    # If user_id is provided, admin is editing another user's data
    if user_id:
        if not request.user.userprofile.user_type == 'admin':
            messages.error(request, 'You do not have permission to edit other users\' data.')
            return redirect('profile')
        user_to_edit = get_object_or_404(User, id=user_id)
    else:
        # User is editing their own data
        user_to_edit = request.user

    if request.method == 'POST':
        form = PersonalDataForm(request.POST, instance=user_to_edit.personal_data)
        if form.is_valid():
            form.save()
            messages.success(request, 'Personal data updated successfully.')
            if user_id:
                return redirect('view_user_profile', user_id=user_id)
            return redirect('profile')
    else:
        form = PersonalDataForm(instance=user_to_edit.personal_data)
    
    context = {
        'form': form,
        'user_to_edit': user_to_edit,
        'is_admin_edit': bool(user_id)
    }
    return render(request, 'accounts/edit_personal_data.html', context)

@login_required
@user_passes_test(is_admin)
def delete_user(request, user_id):
    user_to_delete = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        username = user_to_delete.username
        user_to_delete.delete()
        messages.success(request, f'User {username} has been deleted successfully.')
        return redirect('user_list')
    
    return render(request, 'accounts/delete_user.html', {
        'user_to_delete': user_to_delete
    })

@login_required
@user_passes_test(is_admin)
def user_management(request):
    users = User.objects.all().order_by('-date_joined')
    search_query = request.GET.get('search', '')
    user_type = request.GET.get('user_type', '')

    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(userprofile__id_number__icontains=search_query)
        )

    if user_type:
        users = users.filter(userprofile__user_type=user_type)

    paginator = Paginator(users, 10)  # Show 10 users per page
    page_number = request.GET.get('page')
    users = paginator.get_page(page_number)

    return render(request, 'accounts/user_management.html', {
        'users': users,
    })

@login_required
@user_passes_test(is_admin)
def update_user_profile(request, user_id):
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        profile = user.userprofile
        
        # Update profile fields
        profile.salary = request.POST.get('salary')
        profile.phone_number = request.POST.get('phone_number')
        profile.address = request.POST.get('address')
        profile.save()
        
        messages.success(request, f'Profile updated successfully for {user.get_full_name()}')
        return redirect('user_management')
    
    return redirect('user_management')

@login_required
@user_passes_test(is_admin)
def view_user_profile(request, user_id):
    user = get_object_or_404(User, id=user_id)
    return render(request, 'accounts/view_user_pds.html', {
        'profile_user': user,
        'total_users': User.objects.count(),
        'admin_users': UserProfile.objects.filter(user_type='admin').count(),
        'viewer_users': UserProfile.objects.filter(user_type='viewer').count(),
        'active_today': ActivityLog.objects.filter(
            timestamp__date=timezone.now().date()
        ).values('user').distinct().count(),
        'activity_logs': ActivityLog.objects.filter(user=user).order_by('-timestamp')[:5],
    })
