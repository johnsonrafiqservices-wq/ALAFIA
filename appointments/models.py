from django.db import models
from django.contrib.auth import get_user_model
from patients.models import Patient

User = get_user_model()

class Service(models.Model):
    SERVICE_CATEGORIES = [
        ('physiotherapy', 'Physiotherapy'),
        ('nutrition', 'Nutrition'),
        ('consultation', 'Consultation'),
        ('assessment', 'Assessment'),
        ('treatment', 'Treatment'),
        ('pharmacy', 'Pharmacy'),
    ]
    
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=SERVICE_CATEGORIES)
    description = models.TextField(blank=True)
    duration_minutes = models.IntegerField(default=60)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"
    
    class Meta:
        ordering = ['category', 'name']

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    provider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments_as_provider')
    
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    duration_minutes = models.IntegerField()
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    notes = models.TextField(blank=True, help_text="Appointment notes or special instructions")
    
    # System fields
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_appointments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.patient.get_full_name()} - {self.service.name} on {self.appointment_date} at {self.appointment_time}"
    
    class Meta:
        ordering = ['appointment_date', 'appointment_time']
        unique_together = ['provider', 'appointment_date', 'appointment_time']

class TreatmentSession(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='treatment_session')
    
    # Session details
    chief_complaint = models.TextField(help_text="Main reason for visit")
    assessment_findings = models.TextField(help_text="Clinical assessment findings")
    treatment_provided = models.TextField(help_text="Treatment/interventions provided")
    patient_response = models.TextField(help_text="Patient's response to treatment")
    
    # Progress tracking
    pain_level_before = models.IntegerField(help_text="Pain scale 0-10 before treatment", blank=True, null=True)
    pain_level_after = models.IntegerField(help_text="Pain scale 0-10 after treatment", blank=True, null=True)
    functional_improvement = models.TextField(blank=True, help_text="Functional improvements noted")
    
    # Plan
    home_exercises = models.TextField(blank=True, help_text="Prescribed home exercises")
    recommendations = models.TextField(blank=True, help_text="Recommendations and advice")
    next_appointment_notes = models.TextField(blank=True, help_text="Notes for next appointment")
    
    # Session completion
    session_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"Treatment session for {self.appointment}"
    
    class Meta:
        ordering = ['-appointment__appointment_date']

class NutritionConsultation(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='nutrition_consultation')
    
    # Assessment
    current_diet = models.TextField(help_text="Current dietary habits")
    dietary_restrictions = models.TextField(blank=True, help_text="Allergies, intolerances, preferences")
    health_goals = models.TextField(help_text="Patient's health and nutrition goals")
    
    # Measurements
    current_weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    target_weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    body_fat_percentage = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True)
    
    # Plan
    meal_plan = models.TextField(help_text="Recommended meal plan")
    supplements = models.TextField(blank=True, help_text="Recommended supplements")
    lifestyle_recommendations = models.TextField(blank=True, help_text="Lifestyle and activity recommendations")
    
    # Follow-up
    follow_up_weeks = models.IntegerField(default=4, help_text="Recommended follow-up in weeks")
    consultation_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"Nutrition consultation for {self.appointment}"
    
    class Meta:
        ordering = ['-appointment__appointment_date']


class ReminderSettings(models.Model):
    """Clinic-wide reminder settings"""
    # Timing settings (hours before appointment)
    first_reminder_hours = models.IntegerField(default=48, help_text="Hours before appointment for first reminder")
    second_reminder_hours = models.IntegerField(default=24, help_text="Hours before appointment for second reminder")
    final_reminder_hours = models.IntegerField(default=2, help_text="Hours before appointment for final reminder")
    
    # Notification methods
    email_enabled = models.BooleanField(default=True, help_text="Send email reminders")
    sms_enabled = models.BooleanField(default=True, help_text="Send SMS reminders")
    
    # Recipient settings
    notify_patient = models.BooleanField(default=True, help_text="Send reminders to patients")
    notify_provider = models.BooleanField(default=True, help_text="Send reminders to providers")
    notify_admin = models.BooleanField(default=False, help_text="Send reminders to admin")
    notify_nurse = models.BooleanField(default=False, help_text="Send reminders to nurses")
    notify_receptionist = models.BooleanField(default=True, help_text="Send reminders to receptionists")
    
    # SMS settings (configured in settings.py and .env)
    # Note: SMS provider and credentials are configured in .env file
    # Supported providers: Africa's Talking, People's SMS, SMS Box, Generic HTTP Gateway
    sms_provider_note = models.CharField(
        max_length=500, 
        blank=True, 
        default="Configure SMS in .env file: SMS_PROVIDER, API keys, etc. See SMS_SETUP_GUIDE.md",
        help_text="SMS is configured via environment variables (.env file)"
    )
    
    # Email settings
    reminder_from_email = models.EmailField(blank=True, help_text="Email address for sending reminders")
    admin_emails = models.TextField(blank=True, help_text="Comma-separated admin emails")
    nurse_emails = models.TextField(blank=True, help_text="Comma-separated nurse emails")
    receptionist_emails = models.TextField(blank=True, help_text="Comma-separated receptionist emails")
    
    # System
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Reminder Settings (Updated: {self.updated_at.strftime('%Y-%m-%d %H:%M')})"
    
    class Meta:
        verbose_name = "Reminder Settings"
        verbose_name_plural = "Reminder Settings"
    
    @classmethod
    def get_settings(cls):
        """Get or create singleton settings instance"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings


class AppointmentReminder(models.Model):
    """Track sent appointment reminders"""
    REMINDER_TYPE_CHOICES = [
        ('first', 'First Reminder'),
        ('second', 'Second Reminder'),
        ('final', 'Final Reminder'),
    ]
    
    RECIPIENT_TYPE_CHOICES = [
        ('patient', 'Patient'),
        ('provider', 'Provider'),
        ('admin', 'Admin'),
        ('nurse', 'Nurse'),
        ('receptionist', 'Receptionist'),
    ]
    
    METHOD_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='reminders')
    reminder_type = models.CharField(max_length=10, choices=REMINDER_TYPE_CHOICES)
    recipient_type = models.CharField(max_length=15, choices=RECIPIENT_TYPE_CHOICES)
    method = models.CharField(max_length=10, choices=METHOD_CHOICES)
    
    # Recipient details
    recipient_name = models.CharField(max_length=200)
    recipient_email = models.EmailField(blank=True)
    recipient_phone = models.CharField(max_length=20, blank=True)
    
    # Scheduling
    scheduled_for = models.DateTimeField(help_text="When to send this reminder")
    sent_at = models.DateTimeField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)
    
    # Message content
    message_subject = models.CharField(max_length=200, blank=True)
    message_body = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.get_reminder_type_display()} for {self.appointment.patient.get_full_name()} - {self.get_status_display()}"
    
    class Meta:
        ordering = ['scheduled_for', 'created_at']
        indexes = [
            models.Index(fields=['scheduled_for', 'status']),
            models.Index(fields=['appointment', 'reminder_type']),
        ]
