from django.db import models
from django.contrib.auth import get_user_model
from patients.models import Patient
from appointments.models import Appointment, Service
from decimal import Decimal

User = get_user_model()

class Invoice(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ]
    
    invoice_number = models.CharField(max_length=20, unique=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='invoices')
    
    # Invoice details
    issue_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Amounts
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # Percentage
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Additional info
    notes = models.TextField(blank=True)
    
    # System fields
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def calculate_totals(self):
        """Calculate invoice totals based on line items"""
        line_items = self.line_items.all()
        self.subtotal = sum(item.total_amount for item in line_items)
        self.tax_amount = (self.subtotal * self.tax_rate) / 100
        self.total_amount = self.subtotal + self.tax_amount - self.discount_amount
        self.save()
    
    def get_total_paid(self):
        """Calculate total amount paid for this invoice"""
        return sum(payment.amount for payment in self.payments.filter(status='completed'))
    
    def get_balance_due(self):
        """Calculate remaining balance due"""
        return self.total_amount - self.get_total_paid()
    
    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.patient.get_full_name()}"
    
    class Meta:
        ordering = ['-created_at']

class InvoiceLineItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='line_items')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True)
    
    description = models.CharField(max_length=200)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    def save(self, *args, **kwargs):
        self.total_amount = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        # Recalculate invoice totals
        self.invoice.calculate_totals()
    
    def __str__(self):
        return f"{self.description} - {self.total_amount}"

class Payment(models.Model):
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('check', 'Check'),
        ('bank_transfer', 'Bank Transfer'),
        ('insurance', 'Insurance'),
    ]
    
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    payment_id = models.CharField(max_length=20, unique=True)
    # Invoice is optional to allow general payments recorded against a patient only
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='payments')
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    payment_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    
    # Payment details
    reference_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    
    # System fields
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        # Ensure invoice is None (NULL) if empty, not empty string
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"🔥 MODEL SAVE CALLED - invoice_id BEFORE: '{self.invoice_id}' (type: {type(self.invoice_id)})")
        
        if self.invoice_id == '':
            logger.error(f"Converting empty string to None")
            self.invoice_id = None
        elif self.invoice_id is None:
            logger.error(f"invoice_id is already None - good!")
        
        # Also check if invoice is None but invoice_id is not
        if self.invoice is None and self.invoice_id is not None:
            logger.error(f"⚠️ WARNING: invoice is None but invoice_id is {self.invoice_id} - forcing to None")
            self.invoice_id = None
        
        logger.error(f"🔥 MODEL SAVE - invoice_id AFTER: '{self.invoice_id}' (type: {type(self.invoice_id)})")
        
        super().save(*args, **kwargs)
        logger.error(f"✅ MODEL SAVE SUCCESSFUL!")
    
    def __str__(self):
        return f"Payment {self.payment_id} - UGX {self.amount}"
    
    class Meta:
        ordering = ['-payment_date']

class InsuranceClaim(models.Model):
    CLAIM_STATUS = [
        ('submitted', 'Submitted'),
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('denied', 'Denied'),
        ('paid', 'Paid'),
    ]
    
    claim_number = models.CharField(max_length=20, unique=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='insurance_claims')
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='insurance_claims')
    
    # Insurance details
    insurance_provider = models.CharField(max_length=100)
    policy_number = models.CharField(max_length=50)
    group_number = models.CharField(max_length=50, blank=True)
    
    # Claim details
    claim_amount = models.DecimalField(max_digits=10, decimal_places=2)
    approved_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=CLAIM_STATUS, default='submitted')
    
    submission_date = models.DateField(auto_now_add=True)
    response_date = models.DateField(blank=True, null=True)
    
    notes = models.TextField(blank=True)
    
    # System fields
    submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Claim {self.claim_number} - {self.patient.get_full_name()}"
    
    class Meta:
        ordering = ['-submission_date']

class PaymentPlan(models.Model):
    PLAN_STATUS = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('defaulted', 'Defaulted'),
        ('cancelled', 'Cancelled'),
    ]
    
    plan_id = models.CharField(max_length=20, unique=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='payment_plans')
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payment_plans')
    
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    monthly_payment = models.DecimalField(max_digits=10, decimal_places=2)
    number_of_payments = models.IntegerField()
    payments_made = models.IntegerField(default=0)
    
    start_date = models.DateField()
    status = models.CharField(max_length=20, choices=PLAN_STATUS, default='active')
    
    notes = models.TextField(blank=True)
    
    # System fields
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def remaining_balance(self):
        paid_amount = self.payments_made * self.monthly_payment
        return self.total_amount - paid_amount
    
    def __str__(self):
        return f"Payment Plan {self.plan_id} - {self.patient.get_full_name()}"
    
    class Meta:
        ordering = ['-created_at']
