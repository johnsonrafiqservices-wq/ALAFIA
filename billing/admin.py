from django.contrib import admin
from .models import Invoice, InvoiceLineItem, Payment, InsuranceClaim, PaymentPlan

class InvoiceLineItemInline(admin.TabularInline):
    model = InvoiceLineItem
    extra = 1

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'patient', 'issue_date', 'due_date', 'total_amount', 'status')
    list_filter = ('status', 'issue_date', 'due_date')
    search_fields = ('invoice_number', 'patient__first_name', 'patient__last_name')
    readonly_fields = ('invoice_number', 'subtotal', 'tax_amount', 'total_amount', 'created_at', 'updated_at')
    inlines = [InvoiceLineItemInline]
    
    fieldsets = (
        ('Invoice Information', {
            'fields': ('invoice_number', 'patient', 'due_date', 'status')
        }),
        ('Amounts', {
            'fields': ('subtotal', 'tax_rate', 'tax_amount', 'discount_amount', 'total_amount')
        }),
        ('Additional Information', {
            'fields': ('notes', 'created_by', 'created_at', 'updated_at')
        }),
    )

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_id', 'patient', 'invoice', 'amount', 'payment_method', 'payment_date', 'status')
    list_filter = ('payment_method', 'status', 'payment_date')
    search_fields = ('payment_id', 'patient__first_name', 'patient__last_name', 'reference_number')
    readonly_fields = ('payment_id', 'payment_date', 'created_at')

@admin.register(InsuranceClaim)
class InsuranceClaimAdmin(admin.ModelAdmin):
    list_display = ('claim_number', 'patient', 'insurance_provider', 'claim_amount', 'approved_amount', 'status')
    list_filter = ('status', 'insurance_provider', 'submission_date')
    search_fields = ('claim_number', 'patient__first_name', 'patient__last_name', 'policy_number')
    readonly_fields = ('claim_number', 'submission_date', 'created_at')

@admin.register(PaymentPlan)
class PaymentPlanAdmin(admin.ModelAdmin):
    list_display = ('plan_id', 'patient', 'total_amount', 'monthly_payment', 'payments_made', 'status')
    list_filter = ('status', 'start_date')
    search_fields = ('plan_id', 'patient__first_name', 'patient__last_name')
    readonly_fields = ('plan_id', 'created_at')
