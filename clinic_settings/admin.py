from django.contrib import admin
from .models import ClinicSettings


@admin.register(ClinicSettings)
class ClinicSettingsAdmin(admin.ModelAdmin):
    list_display = ['clinic_name', 'phone', 'email', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('clinic_name', 'logo')
        }),
        ('Contact Information', {
            'fields': ('address', 'phone', 'email', 'website')
        }),
    )
    
    def has_add_permission(self, request):
        # Only allow adding if no settings exist
        return not ClinicSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Don't allow deletion of settings
        return False
