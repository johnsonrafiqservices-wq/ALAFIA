from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import Http404, JsonResponse, HttpResponse
from django.conf import settings
from .models import ClinicSettings
from .forms import ClinicSettingsForm, ThemeCustomizationForm
import os
import shutil
import json
from datetime import datetime


def is_admin_or_superuser(user):
    """Check if user is admin or superuser"""
    return user.is_superuser or (hasattr(user, 'role') and user.role == 'admin')


@login_required
@user_passes_test(is_admin_or_superuser)
def clinic_settings_view(request):
    """View and edit clinic settings"""
    settings = ClinicSettings.get_settings()
    
    if request.method == 'POST':
        form = ClinicSettingsForm(request.POST, request.FILES, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, 'Clinic settings updated successfully!')
            return redirect('clinic_settings:settings')
    else:
        form = ClinicSettingsForm(instance=settings)
    
    context = {
        'form': form,
        'settings': settings,
    }
    return render(request, 'clinic_settings/settings.html', context)


@login_required
@user_passes_test(is_admin_or_superuser)
def theme_customization_view(request):
    """View for customizing theme colors"""
    settings = ClinicSettings.get_settings()
    
    if request.method == 'POST':
        if 'reset_defaults' in request.POST:
            # Reset all colors to defaults
            default_colors = {
                # Primary Colors
                'primary_color': '#1B5E96',
                'primary_dark': '#154a7a',
                'primary_light': '#e6f1fa',
                # Success Colors
                'success_color': '#2E8B57',
                'success_dark': '#236b43',
                'success_light': '#e8f5f0',
                # Accent Colors
                'accent_color': '#00A86B',
                'accent_dark': '#008554',
                'accent_light': '#e6f9f3',
                # Warning Colors
                'warning_color': '#FF8C00',
                'warning_dark': '#e67e00',
                'warning_light': '#fff4e6',
                # Danger Colors
                'danger_color': '#dc2626',
                'danger_dark': '#b91c1c',
                'danger_light': '#fecaca',
                # Info Colors
                'info_color': '#0891b2',
                'info_dark': '#0e7490',
                'info_light': '#cffafe',
                # Secondary Colors
                'secondary_color': '#64748b',
                'secondary_dark': '#475569',
                'secondary_light': '#f1f5f9',
                # Base Colors
                'dark_color': '#1e293b',
                'light_color': '#f8fafc',
                'border_color': '#e2e8f0',
                # Text Colors
                'text_primary': '#1e293b',
                'text_secondary': '#64748b',
                'text_muted': '#94a3b8',
                # Background Colors
                'bg_primary': '#ffffff',
                'bg_secondary': '#f8fafc',
                'bg_tertiary': '#f1f5f9',
                # Chart Colors
                'chart_color_1': '#1B5E96',
                'chart_color_2': '#2E8B57',
                'chart_color_3': '#00A86B',
                'chart_color_4': '#FF8C00',
                'chart_color_5': '#0891b2',
                'chart_color_6': '#dc2626',
            }
            
            for field, value in default_colors.items():
                setattr(settings, field, value)
            settings.save()
            messages.success(request, 'Theme colors have been reset to default values!')
            return redirect('clinic_settings:theme_customization')
        else:
            form = ThemeCustomizationForm(request.POST, instance=settings)
            if form.is_valid():
                form.save()
                messages.success(request, 'Theme colors updated successfully!')
                return redirect('clinic_settings:theme_customization')
    else:
        form = ThemeCustomizationForm(instance=settings)
    
    context = {
        'form': form,
        'settings': settings,
    }
    return render(request, 'clinic_settings/theme_customization.html', context)


@login_required
@user_passes_test(is_admin_or_superuser)
def database_management_view(request):
    """View for database export and import"""
    db_path = settings.DATABASES['default']['NAME']
    db_name = os.path.basename(db_path)
    db_size = os.path.getsize(db_path) if os.path.exists(db_path) else 0
    db_modified = datetime.fromtimestamp(os.path.getmtime(db_path)) if os.path.exists(db_path) else None
    
    context = {
        'db_name': db_name,
        'db_path': str(db_path),
        'db_size': db_size,
        'db_modified': db_modified,
    }
    return render(request, 'clinic_settings/database_management.html', context)


@login_required
@user_passes_test(is_admin_or_superuser)
def database_export_view(request):
    """Export database as a downloadable file"""
    db_path = settings.DATABASES['default']['NAME']
    
    if not os.path.exists(db_path):
        messages.error(request, 'Database file not found.')
        return redirect('clinic_settings:database_management')
    
    # Create filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    db_name = os.path.basename(db_path)
    filename = f"backup_{db_name}_{timestamp}"
    
    # Read the database file
    with open(db_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/x-sqlite3')
    
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    messages.success(request, 'Database exported successfully!')
    return response


@login_required
@user_passes_test(is_admin_or_superuser)
def database_import_view(request):
    """Import database from uploaded file"""
    if request.method != 'POST':
        return redirect('clinic_settings:database_management')
    
    if 'database_file' not in request.FILES:
        messages.error(request, 'No file selected.')
        return redirect('clinic_settings:database_management')
    
    uploaded_file = request.FILES['database_file']
    db_path = settings.DATABASES['default']['NAME']
    
    # Validate file type
    if not (uploaded_file.name.endswith('.sqlite3') or uploaded_file.name.endswith('.db') or uploaded_file.name.endswith('.sqlite')):
        messages.error(request, 'Invalid file type. Please upload a SQLite database file.')
        return redirect('clinic_settings:database_management')
    
    # Create backup of current database
    backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    try:
        shutil.copy2(db_path, backup_path)
    except Exception as e:
        messages.error(request, f'Failed to create backup: {str(e)}')
        return redirect('clinic_settings:database_management')
    
    # Replace current database with uploaded file
    try:
        with open(db_path, 'wb') as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)
        messages.success(request, 'Database imported successfully! A backup of the previous database was created.')
    except Exception as e:
        # Restore from backup if import fails
        try:
            shutil.copy2(backup_path, db_path)
            messages.error(request, f'Import failed: {str(e)}. Original database restored.')
        except:
            messages.error(request, f'Import failed: {str(e)}. Please check the backup file at {backup_path}')
    
    return redirect('clinic_settings:database_management')
