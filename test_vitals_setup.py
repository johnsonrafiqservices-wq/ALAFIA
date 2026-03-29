"""
Test script to verify vital signs recording setup
Run this with: python manage.py shell < test_vitals_setup.py
"""

from patients.models import Patient, VitalSigns
from patients.forms import VitalSignsForm
from django.contrib.auth import get_user_model

User = get_user_model()

print("=" * 60)
print("VITAL SIGNS SETUP TEST")
print("=" * 60)

# Test 1: Check if VitalSigns model fields are nullable
print("\n1. Testing VitalSigns model field configuration...")
from django.db import connection
cursor = connection.cursor()
cursor.execute("PRAGMA table_info(patients_vitalsigns);")
columns = cursor.fetchall()

vital_fields = {col[1]: col[3] for col in columns}  # name: notnull

required_fields = ['height', 'weight']
optional_fields = ['blood_pressure_systolic', 'blood_pressure_diastolic', 
                   'heart_rate', 'temperature', 'respiratory_rate', 'oxygen_saturation']

print("\n   Required fields (should be NOT NULL):")
for field in required_fields:
    if field in vital_fields:
        is_required = vital_fields[field] == 1
        status = "✅" if is_required else "❌"
        print(f"   {status} {field}: {'NOT NULL' if is_required else 'NULL allowed'}")

print("\n   Optional fields (should allow NULL):")
for field in optional_fields:
    if field in vital_fields:
        is_nullable = vital_fields[field] == 0
        status = "✅" if is_nullable else "❌"
        print(f"   {status} {field}: {'NULL allowed' if is_nullable else 'NOT NULL'}")

# Test 2: Check form validation
print("\n2. Testing VitalSignsForm validation...")

# Test with only required fields
test_data = {
    'height': '175',
    'weight': '70'
}

form = VitalSignsForm(test_data)
if form.is_valid():
    print("   ✅ Form validates with only height and weight")
else:
    print("   ❌ Form validation failed!")
    print(f"   Errors: {form.errors}")

# Test with all fields
test_data_full = {
    'height': '175',
    'weight': '70',
    'blood_pressure_systolic': '120',
    'blood_pressure_diastolic': '80',
    'heart_rate': '72',
    'temperature': '36.5',
    'respiratory_rate': '16',
    'oxygen_saturation': '98'
}

form_full = VitalSignsForm(test_data_full)
if form_full.is_valid():
    print("   ✅ Form validates with all fields")
else:
    print("   ❌ Form validation failed with all fields!")
    print(f"   Errors: {form_full.errors}")

# Test 3: Check if patients exist
print("\n3. Checking for test patients...")
patient_count = Patient.objects.count()
print(f"   Total patients in database: {patient_count}")

if patient_count > 0:
    sample_patient = Patient.objects.first()
    print(f"   ✅ Sample patient: {sample_patient.patient_id} - {sample_patient.get_full_name()}")
else:
    print("   ⚠️ No patients found in database")

# Test 4: Check if users exist
print("\n4. Checking for users...")
user_count = User.objects.count()
print(f"   Total users in database: {user_count}")

if user_count > 0:
    sample_user = User.objects.filter(is_staff=True).first()
    if sample_user:
        print(f"   ✅ Sample staff user: {sample_user.username}")
    else:
        print("   ⚠️ No staff users found")
else:
    print("   ⚠️ No users found in database")

# Test 5: Check vital signs records
print("\n5. Checking existing vital signs records...")
vitals_count = VitalSigns.objects.count()
print(f"   Total vital signs records: {vitals_count}")

if vitals_count > 0:
    latest_vital = VitalSigns.objects.latest('recorded_date')
    print(f"   ✅ Latest record:")
    print(f"      Patient: {latest_vital.patient.get_full_name()}")
    print(f"      Height: {latest_vital.height} cm")
    print(f"      Weight: {latest_vital.weight} kg")
    print(f"      BMI: {latest_vital.bmi}")
    print(f"      Recorded by: {latest_vital.recorded_by.username if latest_vital.recorded_by else 'Unknown'}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
