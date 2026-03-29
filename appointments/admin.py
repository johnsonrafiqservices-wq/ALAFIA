from django.contrib import admin
from .models import Service, Appointment, TreatmentSession, NutritionConsultation, ReminderSettings, AppointmentReminder

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'duration_minutes', 'base_price', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'description')

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'service', 'provider', 'appointment_date', 'appointment_time', 'status')
    list_filter = ('status', 'appointment_date', 'service__category', 'provider')
    search_fields = ('patient__first_name', 'patient__last_name', 'patient__patient_id')
    date_hierarchy = 'appointment_date'

@admin.register(TreatmentSession)
class TreatmentSessionAdmin(admin.ModelAdmin):
    list_display = ('appointment', 'session_completed', 'completed_at')
    list_filter = ('session_completed', 'completed_at')
    search_fields = ('appointment__patient__first_name', 'appointment__patient__last_name')

@admin.register(NutritionConsultation)
class NutritionConsultationAdmin(admin.ModelAdmin):
    list_display = ('appointment', 'consultation_completed', 'completed_at')
    list_filter = ('consultation_completed', 'completed_at')
    search_fields = ('appointment__patient__first_name', 'appointment__patient__last_name')

@admin.register(ReminderSettings)
class ReminderSettingsAdmin(admin.ModelAdmin):
    list_display = ('id', 'is_active', 'email_enabled', 'sms_enabled', 'updated_at')
    
    fieldsets = (
        ('Reminder Timing', {
            'fields': ('first_reminder_hours', 'second_reminder_hours', 'final_reminder_hours'),
            'description': 'Set how many hours before the appointment to send each reminder'
        }),
        ('Notification Methods', {
            'fields': ('email_enabled', 'sms_enabled'),
        }),
        ('Recipients', {
            'fields': ('notify_patient', 'notify_provider', 'notify_admin', 'notify_nurse', 'notify_receptionist'),
            'description': 'Select who should receive appointment reminders'
        }),
        ('Email Settings', {
            'fields': ('reminder_from_email', 'admin_emails', 'nurse_emails', 'receptionist_emails'),
            'description': 'Configure email addresses (use comma-separated values for multiple emails)'
        }),
        ('SMS Configuration', {
            'fields': ('sms_provider_note',),
            'description': '''
                <div style="background: #e7f3ff; padding: 15px; border-left: 4px solid #2196F3; margin: 10px 0;">
                    <h3 style="margin-top: 0;">📱 SMS Setup Instructions:</h3>
                    <p><strong>SMS is configured via .env file (not here)</strong></p>
                    <ol>
                        <li><strong>Choose Provider:</strong> Africa's Talking (FREE testing!), People's SMS, SMS Box, or Generic</li>
                        <li><strong>Sign up:</strong> Get free account at <a href="https://africastalking.com/" target="_blank">africastalking.com</a></li>
                        <li><strong>Get API key:</strong> From provider dashboard</li>
                        <li><strong>Add to .env file:</strong> SMS_PROVIDER, API keys, etc.</li>
                        <li><strong>Enable above:</strong> Check "SMS Enabled" checkbox</li>
                    </ol>
                    <p><strong>📚 Full Guide:</strong> See <code>SMS_SETUP_GUIDE.md</code> or <code>START_SMS_HERE.txt</code></p>
                    <p><strong>🧪 Test:</strong> Run <code>python test_sms.py</code></p>
                    <p><strong>💰 Cost:</strong> ~UGX 130 per SMS (Africa's Talking)</p>
                </div>
            ''',
            'classes': ('wide',)
        }),
        ('System', {
            'fields': ('is_active',),
        }),
    )
    
    def has_add_permission(self, request):
        # Only allow one settings instance
        return not ReminderSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Don't allow deletion of settings
        return False

@admin.register(AppointmentReminder)
class AppointmentReminderAdmin(admin.ModelAdmin):
    list_display = ('appointment', 'reminder_type', 'recipient_type', 'method', 'status', 'scheduled_for', 'sent_at')
    list_filter = ('reminder_type', 'recipient_type', 'method', 'status', 'scheduled_for')
    search_fields = ('recipient_name', 'recipient_email', 'recipient_phone', 'appointment__patient__first_name', 'appointment__patient__last_name')
    date_hierarchy = 'scheduled_for'
    readonly_fields = ('created_at', 'sent_at')
    
    fieldsets = (
        ('Appointment & Reminder Info', {
            'fields': ('appointment', 'reminder_type', 'recipient_type', 'method')
        }),
        ('Recipient Details', {
            'fields': ('recipient_name', 'recipient_email', 'recipient_phone')
        }),
        ('Scheduling', {
            'fields': ('scheduled_for', 'sent_at', 'status')
        }),
        ('Message', {
            'fields': ('message_subject', 'message_body')
        }),
        ('Error Info', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_sent', 'mark_as_cancelled']
    
    def mark_as_sent(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='sent', sent_at=timezone.now())
    mark_as_sent.short_description = "Mark selected reminders as sent"
    
    def mark_as_cancelled(self, request, queryset):
        queryset.update(status='cancelled')
    mark_as_cancelled.short_description = "Mark selected reminders as cancelled"
