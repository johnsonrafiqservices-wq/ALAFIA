from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('doctor', 'Doctor/Physiotherapist'),
        ('nutritionist', 'Nutritionist'),
        ('receptionist', 'Receptionist'),
        ('nurse', 'Nurse'),
        ('billing', 'Billing Staff'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='receptionist')
    phone = models.CharField(max_length=15, blank=True)
    employee_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    department = models.CharField(max_length=50, blank=True)
    is_active_employee = models.BooleanField(default=True)
    date_joined_clinic = models.DateField(auto_now_add=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.get_role_display()})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    class Meta:
        db_table = 'accounts_user'


class UserAppPermission(models.Model):
    """Store user-specific app access overrides"""
    ACCESS_CHOICES = [
        ('default', 'Default'),
        ('allow', 'Allow'),
        ('block', 'Block'),
    ]
    
    # Available apps in the system
    APP_CHOICES = [
        ('patients', 'Patients'),
        ('appointments', 'Appointments'),
        ('billing', 'Billing & Finance'),
        ('medical_records', 'Medical Records'),
        ('laboratory', 'Laboratory'),
        ('pharmacy', 'Pharmacy'),
        ('reports', 'Reports & Analytics'),
        ('staff_management', 'Staff Management'),
        ('budget', 'Budget & Planning'),
        ('clinic_settings', 'Clinic Settings'),
        ('inventory', 'Inventory'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='app_permissions')
    app_name = models.CharField(max_length=50, choices=APP_CHOICES)
    access = models.CharField(max_length=10, choices=ACCESS_CHOICES, default='default')
    
    class Meta:
        unique_together = ['user', 'app_name']
        db_table = 'accounts_userapppermission'
    
    def __str__(self):
        return f"{self.user.username} - {self.app_name}: {self.access}"
