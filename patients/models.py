from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator

User = get_user_model()

class Patient(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    BLOOD_TYPE_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]
    
    # Personal Information
    patient_id = models.CharField(max_length=20, unique=True)
    is_visiting_patient = models.BooleanField(default=False, help_text="Check if this is a visiting patient with minimal information")
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$')
    phone = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    email = models.EmailField(blank=True)
    
    # Address Information
    address_line1 = models.CharField(max_length=100, blank=True)
    address_line2 = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=50, blank=True)
    state = models.CharField(max_length=50, blank=True)
    postal_code = models.CharField(max_length=10, blank=True)
    country = models.CharField(max_length=50, default='USA', blank=True)
    
    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    emergency_contact_relationship = models.CharField(max_length=50, blank=True)
    
    # Medical Information
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPE_CHOICES, blank=True)
    allergies = models.TextField(blank=True, help_text="List any known allergies")
    medical_history = models.TextField(blank=True, help_text="Previous medical conditions")
    current_medications = models.TextField(blank=True, help_text="Current medications")
    
    # Insurance Information
    insurance_provider = models.CharField(max_length=100, blank=True)
    insurance_policy_number = models.CharField(max_length=50, blank=True)
    insurance_group_number = models.CharField(max_length=50, blank=True)
    
    # System Information
    registered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='registered_patients')
    registration_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        if self.is_visiting_patient and not (self.first_name and self.last_name):
            return f"Visiting Patient ({self.patient_id})"
        return f"{self.first_name} {self.last_name} ({self.patient_id})"
    
    def get_full_name(self):
        if self.is_visiting_patient and not (self.first_name and self.last_name):
            return "Visiting Patient"
        return f"{self.first_name} {self.last_name}"
    
    def has_complete_name(self):
        """Check if patient has both first and last name"""
        return bool(self.first_name and self.last_name)
    
    def get_age(self):
        if not self.date_of_birth:
            return "Unknown"
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
    
    class Meta:
        ordering = ['last_name', 'first_name']

class VitalSigns(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='vital_signs')
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    recorded_date = models.DateTimeField(auto_now_add=True)
    
    # Vital measurements
    height = models.DecimalField(max_digits=5, decimal_places=2, help_text="Height in cm")
    weight = models.DecimalField(max_digits=5, decimal_places=2, help_text="Weight in kg")
    # Make non-essential measurements optional so users can save just height/weight
    blood_pressure_systolic = models.IntegerField(help_text="Systolic BP", blank=True, null=True)
    blood_pressure_diastolic = models.IntegerField(help_text="Diastolic BP", blank=True, null=True)
    heart_rate = models.IntegerField(help_text="Heart rate (BPM)", blank=True, null=True)
    temperature = models.DecimalField(max_digits=4, decimal_places=1, help_text="Temperature in Celsius", blank=True, null=True)
    respiratory_rate = models.IntegerField(help_text="Breaths per minute", blank=True, null=True)
    oxygen_saturation = models.IntegerField(help_text="SpO2 percentage", blank=True, null=True)
    
    # Additional measurements
    bmi = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True)
    notes = models.TextField(blank=True)
    
    def save(self, *args, **kwargs):
        # Calculate BMI automatically
        if self.height and self.weight:
            height_m = float(self.height) / 100  # Convert cm to meters
            self.bmi = round(float(self.weight) / (height_m ** 2), 1)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Vitals for {self.patient.get_full_name()} on {self.recorded_date.strftime('%Y-%m-%d')}"
    
    class Meta:
        ordering = ['-recorded_date']

class Triage(models.Model):
    PRIORITY_CHOICES = [
        ('1', 'Critical - Immediate'),
        ('2', 'High - Within 15 minutes'),
        ('3', 'Medium - Within 30 minutes'),
        ('4', 'Low - Within 60 minutes'),
        ('5', 'Non-urgent - Within 2 hours'),
    ]
    
    DEPARTMENT_CHOICES = [
        ('physiotherapy', 'Physiotherapy'),
        ('nutrition', 'Nutrition'),
        ('general', 'General Medicine'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='triages')
    triaged_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    triage_date = models.DateTimeField(auto_now_add=True)
    
    # Department routing
    assigned_department = models.CharField(max_length=20, choices=DEPARTMENT_CHOICES, default='general')
    
    chief_complaint = models.TextField(help_text="Primary reason for visit")
    pain_scale = models.IntegerField(help_text="Pain scale 0-10", blank=True, null=True)
    priority_level = models.CharField(max_length=1, choices=PRIORITY_CHOICES)
    
    # Basic triage information
    symptoms = models.TextField(help_text="Current symptoms")
    onset = models.CharField(max_length=100, help_text="When did symptoms start?")
    duration = models.CharField(max_length=100, help_text="How long have symptoms persisted?")
    
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Triage for {self.patient.get_full_name()} - Priority {self.priority_level}"
    
    class Meta:
        ordering = ['-triage_date']

class Assessment(models.Model):
    ASSESSMENT_TYPE_CHOICES = [
        ('first_visit', 'First Visit Assessment'),
        ('follow_up', 'Follow-up Assessment'),
    ]
    
    DEPARTMENT_CHOICES = [
        ('physiotherapy', 'Physiotherapy'),
        ('nutrition', 'Nutrition'),
        ('general', 'General Medicine'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='assessments')
    assessed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    assessment_date = models.DateTimeField(auto_now_add=True)
    
    # Assessment type and department
    assessment_type = models.CharField(max_length=20, choices=ASSESSMENT_TYPE_CHOICES)
    department = models.CharField(max_length=20, choices=DEPARTMENT_CHOICES)
    
    # Link to appointment
    related_appointment = models.ForeignKey('appointments.Appointment', on_delete=models.SET_NULL, null=True, blank=True, related_name='assessments')
    
    # Legacy field - kept for backward compatibility
    related_triage = models.ForeignKey(Triage, on_delete=models.SET_NULL, null=True, blank=True, related_name='assessments')
    
    # Assessment details
    chief_complaint = models.TextField(help_text="Primary reason for visit")
    history_of_present_illness = models.TextField(help_text="Detailed history of current condition")
    
    # Physical examination
    physical_examination = models.TextField(help_text="Physical examination findings")
    mobility_status = models.CharField(max_length=100, blank=True)
    mental_status = models.CharField(max_length=100, blank=True)
    
    # Physiotherapy-specific fields
    pain_location = models.TextField(blank=True, help_text="Location and description of pain")
    functional_assessment = models.TextField(blank=True, help_text="Functional limitations and ADLs")
    range_of_motion = models.TextField(blank=True, help_text="ROM measurements")
    muscle_strength = models.TextField(blank=True, help_text="Muscle strength testing results")
    posture_analysis = models.TextField(blank=True, help_text="Postural assessment findings")
    
    # Nutrition-specific fields
    dietary_history = models.TextField(blank=True, help_text="Dietary intake patterns and history")
    anthropometric_measurements = models.TextField(blank=True, help_text="Body measurements and composition")
    biochemical_data = models.TextField(blank=True, help_text="Laboratory values related to nutrition")
    clinical_signs = models.TextField(blank=True, help_text="Physical signs of nutritional status")
    food_allergies_intolerances = models.TextField(blank=True, help_text="Food allergies and intolerances")
    nutritional_goals = models.TextField(blank=True, help_text="Nutritional objectives and targets")
    
    # Clinical findings
    diagnosis = models.TextField(blank=True, help_text="Clinical diagnosis or impression")
    treatment_plan = models.TextField(blank=True, help_text="Recommended treatment plan")
    
    # Follow-up information
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateField(blank=True, null=True)
    follow_up_instructions = models.TextField(blank=True)
    
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.get_assessment_type_display()} for {self.patient.get_full_name()} - {self.assessment_date.strftime('%Y-%m-%d')}"
    
    class Meta:
        ordering = ['-assessment_date']

# Legacy model - keep for backward compatibility during migration
class TriageAssessment(models.Model):
    PRIORITY_CHOICES = [
        ('1', 'Critical - Immediate'),
        ('2', 'High - Within 15 minutes'),
        ('3', 'Medium - Within 30 minutes'),
        ('4', 'Low - Within 60 minutes'),
        ('5', 'Non-urgent - Within 2 hours'),
    ]
    
    DEPARTMENT_CHOICES = [
        ('physiotherapy', 'Physiotherapy'),
        ('nutrition', 'Nutrition'),
        ('general', 'General Medicine'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='triage_assessments')
    assessed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    assessment_date = models.DateTimeField(auto_now_add=True)
    
    # Department routing
    assigned_department = models.CharField(max_length=20, choices=DEPARTMENT_CHOICES, default='general')
    
    chief_complaint = models.TextField(help_text="Primary reason for visit")
    pain_scale = models.IntegerField(help_text="Pain scale 0-10", blank=True, null=True)
    priority_level = models.CharField(max_length=1, choices=PRIORITY_CHOICES)
    
    # Assessment details
    symptoms = models.TextField(help_text="Current symptoms")
    onset = models.CharField(max_length=100, help_text="When did symptoms start?")
    duration = models.CharField(max_length=100, help_text="How long have symptoms persisted?")
    
    # Physical assessment
    mobility_status = models.CharField(max_length=100, blank=True)
    mental_status = models.CharField(max_length=100, blank=True)
    
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Triage Assessment for {self.patient.get_full_name()} - Priority {self.priority_level}"
    
    class Meta:
        ordering = ['-assessment_date']


class BirthdayWish(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='birthday_wishes')
    year = models.IntegerField(help_text="Year the birthday wish was sent")
    sent_at = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)

    class Meta:
        unique_together = ('patient', 'year')
        ordering = ['-sent_at']

    def __str__(self):
        return f"Birthday wish to {self.patient.get_full_name()} ({self.year})"
