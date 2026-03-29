from django import forms
from .models import LabTest, LabTestRequest, LabTestResult

class LabTestForm(forms.ModelForm):
    class Meta:
        model = LabTest
        fields = ['name', 'code', 'description', 'price', 'currency']

class LabTestRequestForm(forms.ModelForm):
    class Meta:
        model = LabTestRequest
        fields = ['patient', 'test', 'requested_by', 'date_requested', 'status']

class LabTestResultForm(forms.ModelForm):
    class Meta:
        model = LabTestResult
        fields = ['request', 'result', 'date_reported', 'reported_by']
