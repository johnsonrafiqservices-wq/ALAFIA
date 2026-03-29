def labtest_result_add(request):
	if request.method == 'POST':
		form = LabTestResultForm(request.POST)
		if form.is_valid():
			form.save()
			return redirect('laboratory:labtest_results')
	else:
		form = LabTestResultForm()
	return render(request, 'laboratory/labtest_result_add.html', {'form': form})
from django.shortcuts import render, redirect, get_object_or_404
from .models import LabTest, LabTestRequest, LabTestResult
from .forms import LabTestForm, LabTestRequestForm, LabTestResultForm

def labtest_list(request):
	tests = LabTest.objects.all()
	return render(request, 'laboratory/labtest_list.html', {'tests': tests})

def labtest_add(request):
	if request.method == 'POST':
		form = LabTestForm(request.POST)
		if form.is_valid():
			form.save()
			return redirect('laboratory:labtest_list')
	else:
		form = LabTestForm()
	return render(request, 'laboratory/labtest_add.html', {'form': form})

def labtest_request(request):
	if request.method == 'POST':
		form = LabTestRequestForm(request.POST)
		if form.is_valid():
			form.save()
			return redirect('laboratory:labtest_list')
	else:
		form = LabTestRequestForm()
	return render(request, 'laboratory/labtest_request.html', {'form': form})

def labtest_results(request):
	results = LabTestResult.objects.select_related('request', 'request__patient', 'request__test').all()
	return render(request, 'laboratory/labtest_results.html', {'results': results})
