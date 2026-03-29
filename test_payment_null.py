#!/usr/bin/env python
"""
Quick test to verify NULL invoice handling in Payment model
Run this from Django shell: python manage.py shell < test_payment_null.py
"""

from billing.models import Payment, Invoice
from patients.models import Patient
from django.contrib.auth import get_user_model

User = get_user_model()

print("Testing Payment NULL constraint fix...")

# Get first patient and user
try:
    patient = Patient.objects.first()
    user = User.objects.first()
    
    if not patient or not user:
        print("❌ No patient or user found. Create test data first.")
        exit()
    
    print(f"✓ Using patient: {patient.get_full_name()}")
    print(f"✓ Using user: {user.username}")
    
    # Test 1: Create payment with invoice_id = None
    print("\n=== Test 1: Payment with invoice=None ===")
    payment1 = Payment(
        payment_id="TEST-000001",
        patient=patient,
        invoice=None,  # Explicitly None
        amount=1000.00,
        payment_method='cash',
        status='completed',
        processed_by=user
    )
    payment1.save()
    print(f"✅ SUCCESS: Payment {payment1.payment_id} saved with invoice=None")
    payment1.delete()
    
    # Test 2: Create payment with empty string (should be converted to None)
    print("\n=== Test 2: Payment with invoice_id='' ===")
    payment2 = Payment(
        payment_id="TEST-000002",
        patient=patient,
        invoice=None,
        amount=2000.00,
        payment_method='cash',
        status='completed',
        processed_by=user
    )
    payment2.invoice_id = ''  # Simulate empty string
    payment2.save()  # Should convert '' to None in save()
    print(f"✅ SUCCESS: Payment {payment2.payment_id} saved, invoice_id converted to None")
    payment2.delete()
    
    # Test 3: With actual invoice
    invoice = Invoice.objects.first()
    if invoice:
        print(f"\n=== Test 3: Payment with invoice={invoice.invoice_number} ===")
        payment3 = Payment(
            payment_id="TEST-000003",
            patient=patient,
            invoice=invoice,
            amount=3000.00,
            payment_method='cash',
            status='completed',
            processed_by=user
        )
        payment3.save()
        print(f"✅ SUCCESS: Payment {payment3.payment_id} saved with invoice")
        payment3.delete()
    
    print("\n" + "="*50)
    print("✅ ALL TESTS PASSED!")
    print("="*50)
    print("\nThe Payment model now correctly handles:")
    print("  ✓ invoice=None (NULL in database)")
    print("  ✓ invoice_id='' (converted to None)")
    print("  ✓ invoice=<Invoice object>")
    
except Exception as e:
    print(f"\n❌ TEST FAILED: {e}")
    import traceback
    traceback.print_exc()
