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
