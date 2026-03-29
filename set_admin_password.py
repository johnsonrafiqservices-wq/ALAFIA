#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clinic_system.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.get(username='admin')
user.set_password('admin123')
user.role = 'admin'
user.first_name = 'System'
user.last_name = 'Administrator'
user.save()
print('Admin password set to admin123')
