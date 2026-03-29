from django.contrib import admin
from .models import Drug, DrugUsage, CashFlow, Supplier

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
	list_display = ('name', 'country', 'contact')
	search_fields = ('name', 'country')

@admin.register(Drug)
class DrugAdmin(admin.ModelAdmin):
	list_display = ('name', 'atc_code', 'barcode', 'manufacturer', 'batch_number', 'expiry_date', 'quantity', 'unit_price', 'currency', 'country', 'supplier', 'updated_at')
	search_fields = ('name', 'atc_code', 'barcode', 'manufacturer', 'batch_number')
	list_filter = ('country', 'supplier', 'expiry_date')

@admin.register(DrugUsage)
class DrugUsageAdmin(admin.ModelAdmin):
	list_display = ('drug', 'used_quantity', 'usage_type', 'used_for', 'used_by', 'sold_to', 'sale_price', 'currency', 'country', 'date_used')
	list_filter = ('drug', 'usage_type', 'country')

@admin.register(CashFlow)
class CashFlowAdmin(admin.ModelAdmin):
	list_display = ('drug', 'amount', 'currency', 'flow_type', 'description', 'country', 'date')
	list_filter = ('flow_type', 'country')
