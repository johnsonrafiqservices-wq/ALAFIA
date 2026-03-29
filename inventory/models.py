from django.db import models
from django.utils import timezone


class Supplier(models.Model):
	name = models.CharField(max_length=100)
	country = models.CharField(max_length=100)
	contact = models.CharField(max_length=100, blank=True)
	def __str__(self):
		return self.name

class Drug(models.Model):
	name = models.CharField(max_length=100)
	description = models.TextField(blank=True)
	atc_code = models.CharField(max_length=20, blank=True, help_text="WHO ATC code")
	barcode = models.CharField(max_length=50, blank=True)
	manufacturer = models.CharField(max_length=100, blank=True)
	batch_number = models.CharField(max_length=50, blank=True)
	expiry_date = models.DateField(null=True, blank=True)
	quantity = models.PositiveIntegerField(default=0)
	unit_price = models.DecimalField(max_digits=10, decimal_places=2)
	currency = models.CharField(max_length=10, default='UGX')
	country = models.CharField(max_length=100, blank=True)
	supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return f"{self.name} ({self.atc_code})"


class DrugUsage(models.Model):
	USAGE_TYPE = [
		('internal', 'Internal'),
		('sale', 'Sale'),
	]
	drug = models.ForeignKey(Drug, on_delete=models.CASCADE)
	used_quantity = models.PositiveIntegerField()
	usage_type = models.CharField(max_length=10, choices=USAGE_TYPE, default='internal')
	used_for = models.CharField(max_length=255, blank=True)
	used_by = models.CharField(max_length=100, blank=True)
	sold_to = models.CharField(max_length=100, blank=True)
	sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
	currency = models.CharField(max_length=10, default='UGX')
	country = models.CharField(max_length=100, blank=True)
	date_used = models.DateTimeField(default=timezone.now)

	def __str__(self):
		if self.usage_type == 'sale':
			return f"Sold {self.used_quantity} of {self.drug.name} to {self.sold_to}"
		return f"{self.used_quantity} of {self.drug.name} used by {self.used_by}"


class CashFlow(models.Model):
	drug = models.ForeignKey(Drug, on_delete=models.CASCADE, null=True, blank=True)
	amount = models.DecimalField(max_digits=10, decimal_places=2)
	currency = models.CharField(max_length=10, default='UGX')
	flow_type = models.CharField(max_length=10, choices=[('in', 'In'), ('out', 'Out')])
	description = models.CharField(max_length=255, blank=True)
	country = models.CharField(max_length=100, blank=True)
	date = models.DateTimeField(default=timezone.now)

	def __str__(self):
		return f"{self.flow_type} - {self.amount} {self.currency} ({self.description})"
