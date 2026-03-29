from django.db import models
from django.utils import timezone
from patients.models import Patient

class LabTest(models.Model):
	name = models.CharField(max_length=100)
	code = models.CharField(max_length=50, blank=True)
	description = models.TextField(blank=True)
	price = models.DecimalField(max_digits=10, decimal_places=2)
	currency = models.CharField(max_length=10, default='UGX')
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	def __str__(self):
		return self.name

class LabTestRequest(models.Model):
	patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
	test = models.ForeignKey(LabTest, on_delete=models.CASCADE)
	requested_by = models.CharField(max_length=100)
	date_requested = models.DateTimeField(default=timezone.now)
	status = models.CharField(max_length=20, choices=[('pending','Pending'),('completed','Completed')], default='pending')
	def __str__(self):
		return f"{self.test.name} for {self.patient} ({self.status})"

class LabTestResult(models.Model):
	request = models.ForeignKey(LabTestRequest, on_delete=models.CASCADE)
	result = models.TextField()
	date_reported = models.DateTimeField(default=timezone.now)
	reported_by = models.CharField(max_length=100)
	def __str__(self):
		return f"Result for {self.request}"
