from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active_employee', 'date_joined_clinic')
    list_filter = ('role', 'is_active_employee', 'date_joined_clinic', 'is_staff', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'employee_id')
    ordering = ('username',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Clinic Information', {
            'fields': ('role', 'phone', 'employee_id', 'department', 'is_active_employee', 'profile_picture')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Clinic Information', {
            'fields': ('role', 'phone', 'employee_id', 'department', 'is_active_employee')
        }),
    )
