from django.shortcuts import render, redirect, get_object_or_404
from .models import Drug, DrugUsage, CashFlow, Supplier
from .forms import DrugForm, DrugUsageForm, CashFlowForm, SupplierForm

# List all drugs
def drug_list(request):
	drugs = Drug.objects.select_related('supplier').all()
	return render(request, 'inventory/drug_list.html', {'drugs': drugs})

# Add or edit a drug
def drug_edit(request, pk=None):
	drug = get_object_or_404(Drug, pk=pk) if pk else None
	if request.method == 'POST':
		form = DrugForm(request.POST, instance=drug)
		if form.is_valid():
			form.save()
			return redirect('inventory:drug_list')
	else:
		form = DrugForm(instance=drug)
	return render(request, 'inventory/drug_edit.html', {'form': form})

# Add or edit a supplier
def supplier_edit(request, pk=None):
	supplier = get_object_or_404(Supplier, pk=pk) if pk else None
	if request.method == 'POST':
		form = SupplierForm(request.POST, instance=supplier)
		if form.is_valid():
			form.save()
			return redirect('inventory:drug_list')
	else:
		form = SupplierForm(instance=supplier)
	return render(request, 'inventory/supplier_edit.html', {'form': form})

# Record drug usage or sale
def record_usage(request):
	if request.method == 'POST':
		form = DrugUsageForm(request.POST)
		if form.is_valid():
			usage = form.save()
			# Update drug quantity
			usage.drug.quantity -= usage.used_quantity
			usage.drug.save()
			# Record cash flow
			if usage.usage_type == 'sale':
				CashFlow.objects.create(drug=usage.drug, amount=usage.sale_price or 0, currency=usage.currency, flow_type='in', description=f"Sale to {usage.sold_to}", country=usage.country)
			else:
				CashFlow.objects.create(drug=usage.drug, amount=usage.used_quantity * usage.drug.unit_price, currency=usage.currency, flow_type='out', description=f"Used for {usage.used_for}", country=usage.country)
			return redirect('inventory:drug_list')
	else:
		form = DrugUsageForm()
	return render(request, 'inventory/record_usage.html', {'form': form})

# Cash flow list
def cashflow_list(request):
	flows = CashFlow.objects.select_related('drug').all().order_by('-date')
	return render(request, 'inventory/cashflow_list.html', {'flows': flows})

# Expense Dashboard
def expense_dashboard(request):
	from django.db.models import Sum, Count
	from datetime import datetime, timedelta
	
	# Get all expenses (flow_type='out')
	expenses = CashFlow.objects.filter(flow_type='out').order_by('-date')
	
	# Calculate total expenses
	total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or 0
	
	# Get expenses for current month
	now = datetime.now()
	current_month_start = datetime(now.year, now.month, 1)
	current_month_expenses = expenses.filter(
		date__gte=current_month_start
	).aggregate(total=Sum('amount'))['total'] or 0
	
	# Get expenses for last 7 days
	week_ago = now - timedelta(days=7)
	week_expenses = expenses.filter(
		date__gte=week_ago
	).aggregate(total=Sum('amount'))['total'] or 0
	
	# Count total expense transactions
	expense_count = expenses.count()
	
	# Get recent expenses (last 10)
	recent_expenses = expenses[:10]
	
	# Get expense categories (top 5 descriptions)
	expense_categories = expenses.values('description').annotate(
		total=Sum('amount'),
		count=Count('id')
	).order_by('-total')[:5]
	
	context = {
		'total_expenses': total_expenses,
		'current_month_expenses': current_month_expenses,
		'week_expenses': week_expenses,
		'expense_count': expense_count,
		'recent_expenses': recent_expenses,
		'expense_categories': expense_categories,
		'expenses': expenses,
	}
	
	return render(request, 'inventory/expense_dashboard.html', context)
