from django import forms
from .models import Drug, DrugUsage, CashFlow, Supplier

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'country', 'contact']

class DrugForm(forms.ModelForm):
    class Meta:
        model = Drug
        fields = ['name', 'description', 'atc_code', 'barcode', 'manufacturer', 'batch_number', 'expiry_date', 'quantity', 'unit_price', 'currency', 'country', 'supplier']

class DrugUsageForm(forms.ModelForm):
    class Meta:
        model = DrugUsage
        fields = ['drug', 'used_quantity', 'usage_type', 'used_for', 'used_by', 'sold_to', 'sale_price', 'currency', 'country', 'date_used']

class CashFlowForm(forms.ModelForm):
    class Meta:
        model = CashFlow
        fields = ['drug', 'amount', 'currency', 'flow_type', 'description', 'country', 'date']
