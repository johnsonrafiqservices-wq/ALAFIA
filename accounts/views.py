from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, update_session_auth_hash, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.urls import reverse_lazy
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models import Count, Q
from .models import User, UserAppPermission


# Role default access mapping
ROLE_DEFAULT_ACCESS = {
    'admin': ['patients', 'appointments', 'billing', 'medical_records', 'laboratory', 
              'pharmacy', 'reports', 'staff_management', 'budget', 'clinic_settings', 'inventory'],
    'doctor': ['patients', 'appointments', 'medical_records'],
    'nutritionist': ['patients', 'appointments', 'medical_records'],
    'receptionist': ['patients', 'appointments', 'billing'],
    'nurse': ['patients', 'appointments', 'billing', 'medical_records'],
    'billing': ['billing', 'reports'],
}

# App display info
APP_INFO = {
    'patients': {'name': 'Patients', 'icon': 'bi-people', 'color': '#0ea5e9'},
    'appointments': {'name': 'Appointments', 'icon': 'bi-calendar-check', 'color': '#8b5cf6'},
    'billing': {'name': 'Billing & Finance', 'icon': 'bi-credit-card', 'color': '#10b981'},
    'medical_records': {'name': 'Medical Records', 'icon': 'bi-file-medical', 'color': '#f59e0b'},
    'laboratory': {'name': 'Laboratory', 'icon': 'bi-flask', 'color': '#ec4899'},
    'pharmacy': {'name': 'Pharmacy', 'icon': 'bi-capsule', 'color': '#06b6d4'},
    'reports': {'name': 'Reports & Analytics', 'icon': 'bi-graph-up', 'color': '#6366f1'},
    'staff_management': {'name': 'Staff Management', 'icon': 'bi-person-badge', 'color': '#84cc16'},
    'budget': {'name': 'Budget & Planning', 'icon': 'bi-wallet2', 'color': '#14b8a6'},
    'clinic_settings': {'name': 'Clinic Settings', 'icon': 'bi-gear', 'color': '#64748b'},
    'inventory': {'name': 'Inventory', 'icon': 'bi-box-seam', 'color': '#a855f7'},
}

def is_admin_or_superuser(user):
    """Check if user is admin or superuser"""
    return user.is_superuser or (hasattr(user, 'role') and user.role == 'admin')


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('patients:dashboard')

def custom_logout_view(request):
    """Custom logout view that handles both GET and POST requests"""
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('accounts:login')

class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'accounts/password_change.html'
    success_url = reverse_lazy('accounts:profile')
    
    def form_valid(self, form):
        messages.success(self.request, 'Your password has been changed successfully!')
        return super().form_valid(form)

@login_required
def dashboard(request):
    context = {
        'user': request.user,
        'role': request.user.role,
    }
    return render(request, 'dashboard/dashboard.html', context)

@login_required
def profile(request):
    return render(request, 'accounts/profile.html', {'user': request.user})


@login_required
@user_passes_test(is_admin_or_superuser)
def user_permissions_list(request):
    """List all users with their permission counts"""
    users = User.objects.annotate(
        overrides_count=Count('app_permissions', filter=Q(app_permissions__access__in=['allow', 'block']))
    ).order_by('-is_superuser', 'first_name')
    
    total_users = users.count()
    users_with_overrides = users.filter(overrides_count__gt=0).count()
    total_apps = len(APP_INFO)
    
    context = {
        'users': users,
        'total_users': total_users,
        'users_with_overrides': users_with_overrides,
        'total_apps': total_apps,
        'app_info': APP_INFO,
    }
    return render(request, 'accounts/user_permissions_list.html', context)


@login_required
@user_passes_test(is_admin_or_superuser)
def edit_user_permissions(request, user_id):
    """Edit app permissions for a specific user"""
    target_user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        # Clear existing non-default permissions
        UserAppPermission.objects.filter(user=target_user).delete()
        
        # Save new permissions
        for app_name in APP_INFO.keys():
            access = request.POST.get(f'app_{app_name}', 'default')
            if access != 'default':
                UserAppPermission.objects.create(
                    user=target_user,
                    app_name=app_name,
                    access=access
                )
        
        messages.success(request, f'Permissions updated successfully for {target_user.get_full_name()}!')
        return redirect('accounts:user_permissions_list')
    
    # Get current permissions
    user_permissions = {
        perm.app_name: perm.access 
        for perm in UserAppPermission.objects.filter(user=target_user)
    }
    
    # Determine role default access
    role_default_apps = ROLE_DEFAULT_ACCESS.get(target_user.role, [])
    
    # Build apps list with their status
    apps = []
    for app_key, app_data in APP_INFO.items():
        user_override = user_permissions.get(app_key, 'default')
        is_role_default = app_key in role_default_apps
        
        apps.append({
            'key': app_key,
            'name': app_data['name'],
            'icon': app_data['icon'],
            'color': app_data['color'],
            'role_default': is_role_default,
            'user_override': user_override,
            'current_access': 'allow' if user_override == 'allow' else ('block' if user_override == 'block' else ('allow' if is_role_default else 'block')),
        })
    
    # Count permissions by status
    allowed_count = sum(1 for app in apps if app['current_access'] == 'allow')
    
    context = {
        'target_user': target_user,
        'apps': apps,
        'allowed_count': allowed_count,
        'role_default_apps': role_default_apps,
        'role_display': target_user.get_role_display(),
    }
    return render(request, 'accounts/edit_user_permissions.html', context)
