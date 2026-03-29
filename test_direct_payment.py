#!/usr/bin/env python
"""
Test direct payment creation to isolate the issue
Run: python manage.py shell < test_direct_payment.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clinic_system.settings')
django.setup()

from billing.models import Payment
from patients.models import Patient
from django.contrib.auth import get_user_model

User = get_user_model()

print("=" * 60)
print("DIRECT PAYMENT CREATION TEST")
print("=" * 60)

try:
    patient = Patient.objects.first()
    user = User.objects.first()
    
    if not patient or not user:
        print("❌ No patient or user found")
        exit()
    
    print(f"\n✓ Patient: {patient.get_full_name()} (ID: {patient.pk})")
    print(f"✓ User: {user.username}")
    
    # Test 1: Create payment with explicit invoice=None
    print("\n" + "="*60)
    print("TEST 1: Direct Payment with invoice=None")
    print("="*60)
    
    payment = Payment()
    payment.payment_id = "TEST-999999"
    payment.patient = patient
    payment.invoice = None  # Explicitly None
    payment.amount = 9999.00
    payment.payment_method = 'cash'
    payment.status = 'completed'
    payment.processed_by = user
    
    print(f"\nBefore save:")
    print(f"  payment.invoice = {payment.invoice}")
    print(f"  payment.invoice_id = {payment.invoice_id}")
    print(f"  type(payment.invoice_id) = {type(payment.invoice_id)}")
    
    print(f"\nAttempting to save...")
    payment.save()
    
    print(f"\n✅ SUCCESS! Payment saved with ID: {payment.pk}")
    print(f"  payment.invoice = {payment.invoice}")
    print(f"  payment.invoice_id = {payment.invoice_id}")
    
    # Clean up
    payment.delete()
    print(f"\n✓ Test payment deleted")
    
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED!")
    print("="*60)
    print("\nConclusion: The database DOES accept NULL for invoice_id")
    print("The issue must be in the view/form logic, not the database.")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print(f"\nError type: {type(e)}")
    import traceback
    print("\nFull traceback:")
    traceback.print_exc()
    
    print("\n" + "="*60)
    print("If you see 'NOT NULL constraint failed', the database")
    print("schema is wrong. Check the migration.")
    print("="*60)
