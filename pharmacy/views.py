from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import models, transaction
from django.db.models import Sum, F, ExpressionWrapper, DecimalField, Q
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.urls import reverse
from datetime import timedelta
from .models import Medication, Batch, Prescription, StockMovement, Supplier, Category
from .forms import (
    MedicationForm, BatchForm, PrescriptionForm, StockMovementForm, 
    SupplierForm, StockAdjustmentForm, QualityCheckForm
)

def get_sellable_items():
    return Medication.objects.filter(is_active=True).order_by('name')

def get_prescribable_medications():
    return Medication.objects.filter(
        is_active=True,
        item_type='medication'
    ).order_by('name')

@login_required
def inventory_list(request):
    """Display pharmacy inventory."""
    batches = Batch.objects.select_related('medication').filter(is_active=True)
    
    context = {
        'batches': batches,
        'title': 'Pharmacy Inventory'
    }
    return render(request, 'pharmacy/inventory_list.html', context)

class InventoryDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'pharmacy/inventory_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get total medications and batches
        context['total_medications'] = Medication.objects.filter(is_active=True).count()
        context['total_batches'] = Batch.objects.filter(
            is_active=True,
            expiry_date__gt=timezone.now()
        ).count()
        
        # Get low stock items - calculate stock from batches
        from django.db.models import Sum, Q
        low_stock_items = Medication.objects.filter(
            is_active=True
        ).annotate(
            total_stock=Sum('batches__quantity_remaining', filter=Q(batches__is_active=True))
        ).filter(
            Q(total_stock__lte=F('reorder_level')) | Q(total_stock__isnull=True)
        )
        context['low_stock_items'] = low_stock_items
        context['low_stock_count'] = low_stock_items.count()
        
        # Calculate total inventory value
        total_value = Batch.objects.filter(
            is_active=True,
            expiry_date__gt=timezone.now()
        ).aggregate(
            total=ExpressionWrapper(
                Sum(F('quantity_remaining') * F('medication__unit_price')),
                output_field=DecimalField()
            )
        )['total'] or 0
        context['total_value'] = total_value
        
        # Get items expiring in the next 90 days
        expiry_threshold = timezone.now() + timedelta(days=90)
        context['expiring_soon'] = Batch.objects.filter(
            is_active=True,
            expiry_date__gt=timezone.now(),
            expiry_date__lte=expiry_threshold,
            quantity_remaining__gt=0
        ).select_related('medication').order_by('expiry_date')[:10]
        
        # Add data required for modals
        context['medications'] = get_sellable_items()
        context['prescribable_medications'] = get_prescribable_medications()
        context['suppliers'] = Supplier.objects.filter(is_active=True).order_by('name')
        context['categories'] = Category.objects.all().order_by('name')
        from patients.models import Patient
        context['patients'] = Patient.objects.filter(is_active=True).order_by('first_name')
        
        return context

@login_required
def pharmacy_list(request):
    """Main pharmacy dashboard view."""
    # Get counts and summaries
    total_medications = Medication.objects.filter(is_active=True).count()
    total_batches = Batch.objects.filter(is_active=True).count()
    low_stock_count = Batch.objects.filter(
        is_active=True, 
        quantity_remaining__lte=F('medication__reorder_level')
    ).count()
    pending_prescriptions = Prescription.objects.filter(status='pending').count()
    
    # Get latest prescriptions
    recent_prescriptions = Prescription.objects.all().order_by('-prescribed_date')[:5]
    
    # Get low stock items
    low_stock_items = Batch.objects.filter(
        is_active=True, 
        quantity_remaining__lte=F('medication__reorder_level')
    )
    
    context = {
        'total_medications': total_medications,
        'total_batches': total_batches,
        'low_stock_count': low_stock_count,
        'pending_prescriptions': pending_prescriptions,
        'recent_prescriptions': recent_prescriptions,
        'low_stock_items': low_stock_items,
        'title': 'Pharmacy Dashboard'
    }
    return render(request, 'pharmacy/dashboard.html', context)

@login_required
def supplier_list(request):
    """List all suppliers."""
    suppliers = Supplier.objects.all().order_by('name')
    # Add data required for modals
    medications = get_sellable_items()
    prescribable_medications = get_prescribable_medications()
    categories = Category.objects.all().order_by('name')
    from patients.models import Patient
    patients = Patient.objects.filter(is_active=True).order_by('first_name')
    
    return render(request, 'pharmacy/supplier_list.html', {
        'suppliers': suppliers,
        'medications': medications,
        'prescribable_medications': prescribable_medications,
        'categories': categories,
        'patients': patients,
        'title': 'Suppliers'
    })

@login_required
def supplier_create(request):
    """Create a new supplier."""
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            supplier = form.save()
            messages.success(request, f'Supplier {supplier.name} was created successfully.')
            return redirect('pharmacy:suppliers')
    else:
        form = SupplierForm()
    return render(request, 'pharmacy/supplier_form.html', {'form': form, 'title': 'Add Supplier'})

@login_required
def supplier_detail(request, pk):
    """Display supplier details."""
    supplier = get_object_or_404(Supplier, pk=pk)
    return render(request, 'pharmacy/supplier_detail.html', {'supplier': supplier})

@login_required
def supplier_edit(request, pk):
    """Edit an existing supplier."""
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            supplier = form.save()
            messages.success(request, f'Supplier {supplier.name} was updated successfully.')
            return redirect('pharmacy:supplier_detail', pk=supplier.pk)
    else:
        form = SupplierForm(instance=supplier)
    return render(request, 'pharmacy/supplier_form.html', {'form': form, 'title': f'Edit {supplier.name}'})

@login_required
@require_POST
def supplier_toggle_status(request):
    """Toggle supplier active status."""
    supplier_id = request.POST.get('supplier_id')
    if not supplier_id:
        messages.error(request, 'Supplier ID is required')
        return redirect('pharmacy:supplier_list')
    
    try:
        supplier = get_object_or_404(Supplier, pk=supplier_id)
        supplier.is_active = not supplier.is_active
        supplier.save()
        
        status = 'activated' if supplier.is_active else 'deactivated'
        messages.success(request, f'Supplier {supplier.name} has been {status}.')
    except Supplier.DoesNotExist:
        messages.error(request, 'Supplier not found')
    
    return redirect('pharmacy:supplier_list')

@login_required
def quality_check(request, batch_id):
    """Perform quality check on a specific batch."""
    batch = get_object_or_404(Batch, pk=batch_id, is_active=True)
    
    if request.method == 'POST':
        form = QualityCheckForm(request.POST)
        if form.is_valid():
            # Update batch status based on quality check
            condition = form.cleaned_data['physical_condition']
            action_required = form.cleaned_data['action_required']
            
            # Update batch status if issues found
            if condition != 'good' or action_required:
                batch.status = 'quarantine'
                messages.warning(
                    request,
                    'Batch has been placed in quarantine due to quality concerns.'
                )
            else:
                batch.status = 'active'
                messages.success(request, 'Quality check passed successfully.')
            
            # Create quality check record
            quality_check = {
                'batch': batch,
                'checked_by': request.user,
                'physical_condition': condition,
                'packaging_integrity': form.cleaned_data['packaging_integrity'],
                'storage_conditions': form.cleaned_data['storage_conditions'],
                'visual_inspection': form.cleaned_data['visual_inspection'],
                'notes': form.cleaned_data['notes'],
                'action_required': action_required,
                'recommended_action': form.cleaned_data['recommended_action']
            }
            
            # TODO: Save quality check record in QualityCheck model when created
            
            batch.last_quality_check = timezone.now()
            batch.save()
            
            return redirect('pharmacy:batch_list')
    else:
        form = QualityCheckForm()
    
    context = {
        'form': form,
        'batch': batch,
        'title': f'Quality Check - {batch.medication.name} (Batch: {batch.batch_number})'
    }
    return render(request, 'pharmacy/quality_check.html', context)

@login_required
def stock_report(request):
    """Generate comprehensive stock report."""
    # Get query parameters
    status = request.GET.get('status')
    low_stock = request.GET.get('low_stock') == 'true'
    expiring_soon = request.GET.get('expiring_soon') == 'true'
    category = request.GET.get('category')
    
    # Base queryset
    medications = get_sellable_items()
    
    # Apply filters
    if status:
        medications = medications.filter(status=status)
    if low_stock:
        # Annotate with total stock from batches, then filter
        medications = medications.annotate(
            total_stock=Sum('batches__quantity_remaining', filter=Q(batches__is_active=True))
        ).filter(
            Q(total_stock__lte=F('reorder_level')) | Q(total_stock__isnull=True)
        )
    if category:
        medications = medications.filter(category=category)
    
    # Get active batches for each medication
    batches = Batch.objects.filter(
        medication__in=medications,
        is_active=True
    ).select_related('medication', 'supplier')
    
    if expiring_soon:
        expiry_threshold = timezone.now() + timedelta(days=90)
        batches = batches.filter(expiry_date__lte=expiry_threshold)
    
    # Calculate summary statistics
    total_value = batches.aggregate(
        total=ExpressionWrapper(
            Sum(F('quantity_remaining') * F('medication__unit_price')),
            output_field=DecimalField()
        )
    )['total'] or 0
    
    # Get categories for filter
    categories = Medication.objects.values_list('category', flat=True).distinct()
    
    # Group batches by medication for the report
    medication_stock = {}
    for batch in batches:
        med_id = batch.medication_id
        if med_id not in medication_stock:
            medication_stock[med_id] = {
                'medication': batch.medication,
                'total_stock': 0,
                'batches': [],
                'value': 0,
                'suppliers': set()
            }
        
        med_data = medication_stock[med_id]
        med_data['batches'].append(batch)
        med_data['total_stock'] += batch.quantity_remaining
        med_data['value'] += batch.quantity_remaining * batch.medication.unit_price
        med_data['suppliers'].add(batch.supplier.name if batch.supplier else 'Unknown')
    
    context = {
        'title': 'Stock Report',
        'medications': medication_stock.values(),
        'total_value': total_value,
        'categories': categories,
        'filters': {
            'status': status,
            'low_stock': low_stock,
            'expiring_soon': expiring_soon,
            'category': category
        }
    }
    
    return render(request, 'pharmacy/stock_report.html', context)

@login_required
def stock_movement_list(request):
    """List all stock movements."""
    movements = StockMovement.objects.all().order_by('-created_at')
    return render(request, 'pharmacy/stock_movement_list.html', {'movements': movements, 'title': 'Stock Movements'})

@login_required
def stock_adjustment(request, batch_id):
    """Handle stock adjustment for a specific batch."""
    batch = get_object_or_404(Batch, pk=batch_id, is_active=True)
    
    if request.method == 'POST':
        form = StockAdjustmentForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                movement = form.save(commit=False)
                movement.batch = batch
                movement.created_by = request.user
                
                adjustment_type = form.cleaned_data['adjustment_type']
                quantity = form.cleaned_data['quantity']
                
                if adjustment_type == 'decrease' and quantity > batch.quantity_remaining:
                    messages.error(request, 'Cannot decrease more than available quantity')
                    return redirect('pharmacy:stock_adjustment', batch_id=batch_id)
                
                movement.save()
                
                messages.success(
                    request, 
                    f'Successfully {adjustment_type}d stock by {quantity} units'
                )
                return redirect('pharmacy:batch_list')
    else:
        form = StockAdjustmentForm()
    
    context = {
        'form': form,
        'batch': batch,
        'title': f'Adjust Stock - {batch.medication.name} (Batch: {batch.batch_number})'
    }
    return render(request, 'pharmacy/stock_adjustment.html', context)

@login_required
def add_stock(request):
    """Add new stock."""
    if request.method == 'POST':
        form = StockMovementForm(request.POST)
        if form.is_valid():
            movement = form.save(commit=False)
            movement.movement_type = 'in'
            movement.created_by = request.user
            movement.save()
            batch = movement.batch
            messages.success(request, f'Added {movement.quantity} units to batch {batch.batch_number}')
            return redirect('pharmacy:stock_movement_list')
    else:
        form = StockMovementForm()
    return render(request, 'pharmacy/stock_form.html', {'form': form, 'title': 'Add Stock'})

@login_required
def medication_list(request):
    """Display list of medications."""
    # Get filter parameters
    search = request.GET.get('search', '')
    category = request.GET.get('category', '')
    form_type = request.GET.get('form', '')
    stock_status = request.GET.get('stock_status', '')

    # Base queryset (used for summaries and filtering)
    base_medications = get_sellable_items().annotate(
        total_stock=Sum('batches__quantity_remaining', filter=Q(batches__is_active=True))
    )

    # Apply filters
    if search:
        medications = medications.filter(
            Q(name__icontains=search) |
            Q(generic_name__icontains=search)
        )
    if category:
        medications = medications.filter(category=category)
    if form_type:
        medications = medications.filter(form=form_type)
    if stock_status == 'low':
        # Annotate with total stock from batches, then filter
        medications = medications.annotate(
            total_stock=Sum('batches__quantity_remaining', filter=Q(batches__is_active=True))
        ).filter(
            Q(total_stock__lte=F('reorder_level')) | Q(total_stock__isnull=True)
        )
    elif stock_status == 'out':
        # Filter for medications with no stock
        medications = medications.annotate(
            total_stock=Sum('batches__quantity_remaining', filter=Q(batches__is_active=True))
        ).filter(
            Q(total_stock=0) | Q(total_stock__isnull=True)
        )

    # Get categories and form choices for filters
    categories = Category.objects.all()
    form_choices = Medication.FORM_CHOICES

    # Compute hero stats
    total_active_medications = base_medications.count()
    low_stock_total = base_medications.filter(
        Q(total_stock__lte=F('reorder_level')) | Q(total_stock__isnull=True)
    ).count()
    out_of_stock_total = base_medications.filter(
        Q(total_stock__lte=0) | Q(total_stock__isnull=True)
    ).count()

    # Add data required for modals
    suppliers = Supplier.objects.filter(is_active=True).order_by('name')
    from patients.models import Patient
    patients = Patient.objects.filter(is_active=True).order_by('first_name')

    context = {
        'medications': medications,
        'prescribable_medications': get_prescribable_medications(),
        'categories': categories,
        'form_choices': form_choices,
        'search': search,
        'category_filter': category,
        'form_filter': form_type,
        'stock_status': stock_status,
        'suppliers': suppliers,
        'patients': patients,
        'title': 'Pharmacy Items',
        'total_active_medications': base_medications.count(),
        'low_stock_total': base_medications.filter(
            Q(total_stock__lte=F('reorder_level')) | Q(total_stock__isnull=True)
        ).count(),
        'out_of_stock_total': base_medications.filter(
            Q(total_stock__lte=0) | Q(total_stock__isnull=True)
        ).count(),
        'last_refreshed': timezone.now(),
    }
    return render(request, 'pharmacy/item_list.html', context)

@login_required
def sales_report(request):
    """Sales Report - Using Pharmacy Stock Movements"""
    from django.db.models import Sum, Count, Avg, F, DecimalField, ExpressionWrapper
    from django.db.models.functions import TruncDate
    from datetime import timedelta
    
    # Get date range from request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    today = timezone.now().date()
    if not start_date:
        start_date = (today - timedelta(days=30)).strftime('%Y-%m-%d')
    if not end_date:
        end_date = today.strftime('%Y-%m-%d')
    
    # Filter sales by date range
    sales = StockMovement.objects.filter(
        movement_type='out',
        reference__icontains='SALE',
        created_at__date__gte=start_date,
        created_at__date__lte=end_date
    ).select_related('batch__medication', 'created_by')
    
    # Annotate with revenue
    sales_with_revenue = sales.annotate(
        revenue=ExpressionWrapper(
            F('quantity') * F('batch__selling_price'),
            output_field=DecimalField(max_digits=12, decimal_places=2)
        )
    )
    
    # Summary statistics
    total_sales = sales.count()
    total_revenue = sales_with_revenue.aggregate(total=Sum('revenue'))['total'] or 0
    total_quantity = sales.aggregate(total=Sum('quantity'))['total'] or 0
    avg_sale_value = sales_with_revenue.aggregate(avg=Avg('revenue'))['avg'] or 0
    
    # Sales by item - First annotate revenue on each record, then aggregate
    sales_by_item_raw = sales_with_revenue.values(
        'batch__medication__name'
    ).annotate(
        quantity=Sum('quantity'),
        revenue=Sum('revenue'),
        count=Count('id')
    ).order_by('-revenue')
    
    # Convert to list to ensure it's evaluated
    sales_by_item = list(sales_by_item_raw)
    
    # Daily sales trend - First annotate revenue, then group by date
    daily_sales_raw = sales_with_revenue.annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        count=Count('id'),
        revenue=Sum('revenue')
    ).order_by('date')
    
    # Convert to list to ensure it's evaluated
    daily_sales = list(daily_sales_raw)
    
    # Prepare JSON-serializable data for charts
    import json
    from decimal import Decimal
    
    # Convert dates and decimals for JSON
    daily_sales_json = []
    for item in daily_sales:
        daily_sales_json.append({
            'date': item['date'].strftime('%Y-%m-%d') if item['date'] else '',
            'count': item['count'],
            'revenue': float(item['revenue']) if item['revenue'] else 0
        })
    
    sales_by_item_json = []
    for item in sales_by_item:
        sales_by_item_json.append({
            'batch__medication__name': item['batch__medication__name'],
            'quantity': item['quantity'],
            'revenue': float(item['revenue']) if item['revenue'] else 0,
            'count': item['count']
        })
    
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'total_sales': total_sales,
        'total_revenue': total_revenue,
        'total_quantity': total_quantity,
        'avg_sale_value': avg_sale_value,
        'sales_by_item': sales_by_item,
        'daily_sales': daily_sales,
        'daily_sales_json': json.dumps(daily_sales_json),
        'sales_by_item_json': json.dumps(sales_by_item_json),
    }
    return render(request, 'pharmacy/sales_report.html', context)

@login_required
def record_sale_ajax(request):
    """Enhanced Record Sale AJAX - Supports walk-in, patient sales, and prescription dispensing"""
    if request.method == 'POST':
        try:
            print("record_sale_ajax called")  # Debug
            print(f"POST data: {request.POST}")  # Debug
            
            # Get form data - handle both batch_id and batch parameter names
            batch_id = request.POST.get('batch') or request.POST.get('batch_id')
            quantity = request.POST.get('quantity', '0')
            sale_type = request.POST.get('sale_type', 'walkin')
            customer_info = request.POST.get('customer_info', '')
            notes = request.POST.get('notes', '')
            
            print(f"Batch ID: {batch_id}, Quantity: {quantity}, Sale Type: {sale_type}")  # Debug
            
            # Validate and convert quantity
            try:
                quantity = int(quantity) if quantity else 0
            except (ValueError, TypeError):
                quantity = 0
            
            # For prescriptions, if quantity is invalid, we'll get it from the prescription later
            if sale_type == 'prescription' and quantity <= 0:
                print("⚠️ Quantity is 0 for prescription - will use prescription quantity")
                quantity = 1  # Temporary, will be updated from prescription
            elif quantity <= 0:
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid quantity value. Please enter a valid quantity.'
                })
            
            # Validate inputs (skip batch validation for prescriptions)
            if sale_type != 'prescription' and not batch_id:
                return JsonResponse({
                    'success': False,
                    'message': 'Please provide valid batch and quantity.'
                })
            
            # Get the batch (for prescriptions, batch might be determined later from prescription)
            batch = None
            if batch_id:
                try:
                    batch = Batch.objects.select_related('medication').get(id=batch_id, is_active=True)
                    print(f"Batch found: {batch.batch_number}, Stock: {batch.quantity_remaining}")  # Debug
                    
                    # Check if enough stock
                    if batch.quantity_remaining < quantity:
                        return JsonResponse({
                            'success': False,
                            'message': f'Insufficient stock. Only {batch.quantity_remaining} units available.'
                        })
                except Batch.DoesNotExist:
                    if sale_type != 'prescription':
                        return JsonResponse({
                            'success': False,
                            'message': 'Invalid batch selected.'
                        })
                    # For prescriptions, batch will be determined from prescription medication
                    print("⚠️ No batch_id provided for prescription - will determine from prescription")
            
            # Initialize variables
            customer_name = customer_info if customer_info else 'Walk-in Customer'
            patient = None
            prescription = None
            prescription_dispensed = False
            
            # Handle different sale types
            if sale_type == 'patient':
                # Patient sale
                patient_id = request.POST.get('patient_id')
                if not patient_id:
                    return JsonResponse({
                        'success': False,
                        'message': 'Please select a patient.'
                    })
                
                from patients.models import Patient
                patient = Patient.objects.get(id=patient_id)
                customer_name = f'{patient.patient_id} - {patient.get_full_name()}'
                
            elif sale_type == 'prescription':
                # Prescription dispensing (supports both legacy and multi-medication prescriptions)
                prescription_id = request.POST.get('prescription_id')
                if not prescription_id:
                    return JsonResponse({
                        'success': False,
                        'message': 'Please select a prescription.'
                    })
                
                prescription = Prescription.objects.select_related('patient', 'medication').get(id=prescription_id)
                
                # Check if prescription has already been dispensed
                if prescription.status == 'dispensed':
                    return JsonResponse({
                        'success': False,
                        'message': 'This prescription has already been dispensed.'
                    })
                
                # If no batch was provided, try to find one based on the prescription
                if not batch:
                    # Determine which medication we need
                    prescription_items = prescription.items.all()
                    if prescription_items.exists():
                        # Multi-medication - use first item's medication
                        medication = prescription_items.first().medication
                        quantity = prescription_items.first().quantity
                    elif prescription.medication:
                        # Legacy single medication
                        medication = prescription.medication
                        quantity = prescription.quantity or quantity
                    else:
                        return JsonResponse({
                            'success': False,
                            'message': 'Invalid prescription: no medication specified.'
                        })
                    
                    # Find an available batch for this medication
                    batch = Batch.objects.filter(
                        medication=medication,
                        is_active=True,
                        quantity_remaining__gte=quantity
                    ).order_by('expiry_date').first()
                    
                    if not batch:
                        return JsonResponse({
                            'success': False,
                            'message': f'No available stock for {medication.name}. Please add stock first.'
                        })
                    
                    print(f"✅ Auto-selected batch {batch.batch_number} for prescription medication {medication.name}")
                
                # Check if this is a multi-medication prescription
                prescription_items = prescription.items.all()
                if prescription_items.exists():
                    # Multi-medication prescription - must dispense all items together
                    # Validate that the selected medication and batch match one of the prescription items
                    matching_item = prescription_items.filter(medication_id=batch.medication.id).first()
                    if not matching_item:
                        return JsonResponse({
                            'success': False,
                            'message': f'The selected medication ({batch.medication.name}) is not part of this prescription.'
                        })
                    
                    # Note: Quantity validation relaxed to allow flexible dispensing
                    # The frontend auto-populates the correct quantity
                    # But pharmacist may need to adjust for partial dispensing, stock limitations, etc.
                    if quantity > matching_item.quantity * 2:  # Only warn if drastically different
                        return JsonResponse({
                            'success': False,
                            'message': f'Quantity warning: Prescription requires {matching_item.quantity} units, you entered {quantity} units. Please verify.'
                        })
                    
                    # For multi-medication prescriptions, user must dispense all medications
                    # This is just one item - check if all items have been dispensed
                    # (We'll mark prescription as dispensed after all items are processed)
                    patient = prescription.patient
                    customer_name = f'{patient.patient_id} - {patient.get_full_name()}' if patient else 'Unknown Patient'
                else:
                    # Legacy single-medication prescription
                    if not prescription.medication:
                        return JsonResponse({
                            'success': False,
                            'message': 'Invalid prescription: no medication specified.'
                        })
                    
                    # Validate that the selected medication matches the prescription
                    if batch.medication.id != prescription.medication.id:
                        return JsonResponse({
                            'success': False,
                            'message': f'Medication mismatch. Prescription is for {prescription.medication.name}, you selected {batch.medication.name}.'
                        })
                    
                    # Note: Quantity validation removed to allow flexible dispensing
                    # The frontend auto-populates the correct quantity, but validation was causing issues
                    # Pharmacist can adjust quantity if needed (partial dispensing, etc.)
                    
                    patient = prescription.patient
                    customer_name = f'{patient.patient_id} - {patient.get_full_name()}' if patient else 'Unknown Patient'
            
            # Create stock movement for sale
            reference = f'SALE-{sale_type.upper()}-{timezone.now().strftime("%Y%m%d%H%M%S")}'
            print(f"Creating stock movement: {reference}")  # Debug
            
            stock_movement = StockMovement.objects.create(
                batch=batch,
                movement_type='out',
                quantity=quantity,
                reference=reference,
                notes=notes or f'{sale_type.title()} sale to {customer_name}',
                created_by=request.user
            )
            print(f"Stock movement created: ID {stock_movement.id}")  # Debug
            
            # Calculate revenue
            revenue = quantity * batch.selling_price
            print(f"Revenue calculated: {revenue}")  # Debug
            
            # If this is prescription dispensing, check if we should mark prescription as dispensed
            if prescription:
                # For multi-medication prescriptions, only mark as dispensed if ALL items have been processed
                prescription_items = prescription.items.all()
                if prescription_items.exists():
                    # Multi-medication prescription
                    # For now, we're dispensing one medication at a time through sales modal
                    # The prescription will remain "pending" until all items are dispensed via the proper dispense view
                    # This is just a single-item sale from a multi-med prescription
                    prescription_dispensed = False
                    message_note = ' Note: This prescription has multiple medications. Use the "Dispense" button to dispense all medications together.'
                else:
                    # Legacy single-medication prescription - mark as fully dispensed
                    prescription.status = 'dispensed'
                    prescription.dispensed_by = request.user
                    prescription.dispensed_date = timezone.now()
                    prescription.save()
                    prescription_dispensed = True
                    message_note = ''
            
            # Build success message
            if sale_type == 'prescription':
                if prescription_items.exists():
                    message = f'Item dispensed: {quantity} units of {batch.medication.name} to {patient.get_full_name() if patient else "patient"}.{message_note}'
                else:
                    message = f'Prescription dispensed successfully! {quantity} units of {batch.medication.name} dispensed to {patient.get_full_name() if patient else "patient"}.'
            elif sale_type == 'patient':
                message = f'Sale recorded successfully! {quantity} units of {batch.medication.name} sold to patient {patient.get_full_name()}.'
            else:
                message = f'Sale recorded successfully! {quantity} units of {batch.medication.name} sold.'
            
            print(f"Sale successful: {message}")  # Debug
            
            response_data = {
                'success': True,
                'message': message,
                'prescription_dispensed': prescription_dispensed,
                'data': {
                    'sale_type': sale_type,
                    'medication': batch.medication.name,
                    'quantity': quantity,
                    'revenue': float(revenue),
                    'remaining_stock': batch.quantity_remaining,
                    'customer': customer_name,
                    'patient_id': patient.id if patient else None,
                    'patient_identifier': patient.patient_id if patient else None,
                    'prescription_id': prescription.id if prescription else None,
                    'stock_movement_id': stock_movement.id,
                    'unit_price': float(batch.selling_price)
                }
            }
            print(f"Returning response: {response_data}")  # Debug
            return JsonResponse(response_data)
            
        except Batch.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Batch not found or inactive.'
            })
        except Prescription.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Prescription not found or already dispensed.'
            })
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'success': False,
                'message': f'Error recording sale: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method.'
    })

@login_required
def add_sale_to_invoice_ajax(request):
    """Add a medication sale to a patient's invoice"""
    if request.method == 'POST':
        try:
            stock_movement_id = request.POST.get('stock_movement_id')
            patient_id = request.POST.get('patient_id')
            
            if not stock_movement_id or not patient_id:
                return JsonResponse({
                    'success': False,
                    'message': 'Missing required information.'
                })
            
            # Get the stock movement
            stock_movement = StockMovement.objects.select_related('batch__medication').get(
                id=stock_movement_id
            )
            
            # Get or create patient
            from patients.models import Patient
            patient = Patient.objects.get(id=patient_id)
            
            # Get or create Pharmacy Sale service
            from appointments.models import Service
            from datetime import timedelta
            
            pharmacy_service, created = Service.objects.get_or_create(
                name='Medication Sale',
                defaults={
                    'category': 'pharmacy',  # Correct category
                    'duration_minutes': 15,  # Correct field name
                    'base_price': 0,  # Correct field name - Price will be set per item
                    'description': 'Pharmacy medication sale'
                }
            )
            
            # Get or create draft invoice for patient
            from billing.models import Invoice, InvoiceLineItem
            
            # Look for existing draft invoice
            draft_invoice = Invoice.objects.filter(
                patient=patient,
                status='draft'
            ).first()
            
            if not draft_invoice:
                # Create new draft invoice
                invoice_number = f"INV-{timezone.now().strftime('%Y%m%d%H%M%S')}"
                due_date = timezone.now().date() + timedelta(days=30)
                
                draft_invoice = Invoice.objects.create(
                    invoice_number=invoice_number,
                    patient=patient,
                    due_date=due_date,
                    status='draft',
                    created_by=request.user
                )
            
            # Create invoice line item for the medication sale
            medication = stock_movement.batch.medication
            unit_price = stock_movement.batch.selling_price
            quantity = stock_movement.quantity
            description = f"{medication.name} - Batch: {stock_movement.batch.batch_number}"
            
            line_item = InvoiceLineItem.objects.create(
                invoice=draft_invoice,
                service=pharmacy_service,
                description=description,
                quantity=quantity,
                unit_price=unit_price,
                total_amount=quantity * unit_price
            )
            
            return JsonResponse({
                'success': True,
                'message': f'Sale added to invoice {draft_invoice.invoice_number} successfully!',
                'data': {
                    'invoice_id': draft_invoice.id,
                    'invoice_number': draft_invoice.invoice_number,
                    'line_item_id': line_item.id,
                    'amount': float(line_item.total_amount)
                }
            })
            
        except StockMovement.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Sale record not found.'
            })
        except Patient.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Patient not found.'
            })
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'success': False,
                'message': f'Error adding sale to invoice: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method.'
    })

@login_required
def get_medications_ajax(request):
    """Get list of active medications for dropdowns"""
    try:
        print("get_medications_ajax called")  # Debug
        medications = get_sellable_items()
        print(f"Found {medications.count()} sellable items")  # Debug
        
        medications_list = []
        for med in medications:
            medications_list.append({
                'id': med.id,
                'name': med.name,
                'generic_name': med.generic_name,
                'form': med.form,
                'strength': med.strength,
                'item_type': med.item_type,
                'item_type_display': med.get_item_type_display(),
                'form_display': med.get_form_display() if med.form else ''
            })
        
        print(f"Returning {len(medications_list)} sellable items")  # Debug
        return JsonResponse({
            'success': True,
            'medications': medications_list
        })
    except Exception as e:
        print(f"Error in get_medications_ajax: {str(e)}")  # Debug
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': str(e)
        })


@login_required
def get_batches_ajax(request):
    """Get available batches for a medication"""
    try:
        medication_id = request.GET.get('medication_id')
        print(f"get_batches_ajax called for medication_id: {medication_id}")  # Debug
        
        if not medication_id:
            return JsonResponse({
                'success': False,
                'message': 'Medication ID is required'
            })
        
        # Get active batches with stock
        batches = Batch.objects.filter(
            medication_id=medication_id,
            is_active=True,
            quantity_remaining__gt=0,
            expiry_date__gte=timezone.now().date()
        ).order_by('expiry_date')
        
        print(f"Found {batches.count()} batches for medication {medication_id}")  # Debug
        
        batches_list = []
        for batch in batches:
            batches_list.append({
                'id': batch.id,
                'batch_number': batch.batch_number,
                'current_stock': batch.quantity_remaining,
                'expiry_date': batch.expiry_date.strftime('%Y-%m-%d'),
                'selling_price': str(batch.selling_price),
                'cost_price': str(batch.cost_price)
            })
        
        print(f"Returning {len(batches_list)} batches")  # Debug
        return JsonResponse({
            'success': True,
            'batches': batches_list
        })
    except Exception as e:
        print(f"Error in get_batches_ajax: {str(e)}")  # Debug
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': str(e)
        })


@login_required
def prescription_print(request, prescription_id):
    """Generate printable prescription document"""
    try:
        prescription = Prescription.objects.select_related(
            'patient', 'medication', 'prescribed_by', 'dispensed_by'
        ).get(id=prescription_id)
        
        # Get clinic settings if available
        try:
            from clinic_settings.models import ClinicSettings
            clinic_settings = ClinicSettings.objects.first()
        except:
            clinic_settings = None
        
        context = {
            'prescription': prescription,
            'clinic_settings': clinic_settings,
            'now': timezone.now()
        }
        
        return render(request, 'pharmacy/prescription_print.html', context)
        
    except Prescription.DoesNotExist:
        messages.error(request, 'Prescription not found.')
        return redirect('pharmacy:prescription_list')
    except Exception as e:
        messages.error(request, f'Error generating prescription: {str(e)}')
        return redirect('pharmacy:prescription_list')


@login_required
def prescription_download_pdf(request, prescription_id):
    """Generate and download prescription as PDF"""
    try:
        prescription = Prescription.objects.select_related(
            'patient', 'medication', 'prescribed_by', 'dispensed_by'
        ).get(id=prescription_id)
        
        # Get clinic settings
        try:
            from clinic_settings.models import ClinicSettings
            clinic_settings = ClinicSettings.objects.first()
        except:
            clinic_settings = None
        
        # Generate PDF
        from django.template.loader import render_to_string
        from django.http import HttpResponse
        from django.conf import settings
        import os
        
        # Build absolute logo path for PDF
        logo_path = None
        if clinic_settings and clinic_settings.logo:
            logo_path = os.path.join(settings.MEDIA_ROOT, str(clinic_settings.logo))
        
        context = {
            'prescription': prescription,
            'clinic_settings': clinic_settings,
            'now': timezone.now(),
            'logo_path': logo_path,
            'for_pdf': True
        }
        
        html_content = render_to_string('pharmacy/prescription_print.html', context)
        
        # Try to generate PDF
        try:
            from xhtml2pdf import pisa
            from io import BytesIO
            
            # Define link callback to resolve file paths
            def link_callback(uri, rel):
                if uri.startswith('http://') or uri.startswith('https://'):
                    return uri
                if uri.startswith(settings.MEDIA_URL):
                    path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ''))
                elif uri.startswith(settings.STATIC_URL):
                    path = os.path.join(settings.STATIC_ROOT or settings.BASE_DIR / 'static', 
                                       uri.replace(settings.STATIC_URL, ''))
                else:
                    path = uri
                
                if not os.path.isfile(path):
                    return uri
                return path
            
            pdf_file = BytesIO()
            pisa_status = pisa.CreatePDF(html_content, dest=pdf_file, link_callback=link_callback)
            
            if not pisa_status.err:
                pdf_file.seek(0)
                response = HttpResponse(pdf_file.getvalue(), content_type='application/pdf')
                filename = f'Prescription_RX-{prescription.id:05d}_{prescription.patient.get_full_name().replace(" ", "_")}.pdf'
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                return response
            else:
                messages.error(request, 'PDF generation failed.')
                return redirect('pharmacy:prescription_print', prescription_id=prescription_id)
                
        except ImportError:
            messages.error(request, 'PDF library not available. Please install xhtml2pdf.')
            return redirect('pharmacy:prescription_print', prescription_id=prescription_id)
        except Exception as e:
            messages.error(request, f'PDF generation error: {str(e)}')
            return redirect('pharmacy:prescription_print', prescription_id=prescription_id)
        
    except Prescription.DoesNotExist:
        messages.error(request, 'Prescription not found.')
        return redirect('pharmacy:prescription_list')
    except Exception as e:
        messages.error(request, f'Error processing PDF download: {str(e)}')
        return redirect('pharmacy:prescription_list')


@login_required
def medication_create(request):
    if request.method == 'POST':
        form = MedicationForm(request.POST)
        if form.is_valid():
            medication = form.save()
            messages.success(request, f'Item "{medication.name}" was created successfully.')
            return redirect('pharmacy:medication_list')
    else:
        form = MedicationForm()
    return render(request, 'pharmacy/item_form.html', {'form': form, 'title': 'Add New Pharmacy Item'})

@login_required
def medication_edit(request, pk):
    medication = get_object_or_404(Medication, pk=pk)
    if request.method == 'POST':
        form = MedicationForm(request.POST, instance=medication)
        if form.is_valid():
            medication = form.save()
            messages.success(request, f'Item "{medication.name}" was updated successfully.')
            return redirect('pharmacy:medication_list')
    else:
        form = MedicationForm(instance=medication)
    return render(request, 'pharmacy/item_form.html', {'form': form, 'medication': medication, 'title': f'Edit {medication.name}'})

@login_required
def medication_detail(request, pk):
    medication = get_object_or_404(Medication, pk=pk)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'id': medication.id,
            'name': medication.name,
            'generic_name': medication.generic_name,
            'item_type': medication.item_type,
            'category': medication.category_id,
            'strength': medication.strength,
            'form': medication.form,
            'manufacturer': medication.manufacturer,
            'unit_price': float(medication.unit_price),
            'unit_of_measure': medication.unit_of_measure,
            'reorder_level': medication.reorder_level,
            'storage_instructions': medication.storage_instructions,
            'requires_prescription': medication.requires_prescription,
            'is_active': medication.is_active,
            'notes': medication.notes,
        })

    from .models import PrescriptionItem
    from patients.models import Patient

    batches = medication.batches.filter(is_active=True).order_by('expiry_date')
    stock_value = batches.aggregate(
        total=Sum(
            ExpressionWrapper(
                F('quantity_remaining') * F('selling_price'),
                output_field=DecimalField(max_digits=12, decimal_places=2)
            )
        )
    )['total'] or 0
    all_patients = Patient.objects.filter(is_active=True).order_by('first_name', 'last_name')
    prescription_ids = PrescriptionItem.objects.filter(medication=medication).values_list('prescription_id', flat=True)
    prescriptions = Prescription.objects.filter(
        Q(id__in=prescription_ids) | Q(medication=medication)
    ).select_related('patient', 'prescribed_by').prefetch_related('items__medication').distinct().order_by('-prescribed_date')
    context = {
        'medication': medication,
        'batches': batches,
        'total_stock': medication.current_stock,
        'stock_value': stock_value,
        'batches_count': batches.count(),
        'prescriptions': prescriptions[:20],
        'prescriptions_count': prescriptions.count(),
        'patients': all_patients,
        'all_patients': all_patients,
        'medications': get_sellable_items(),
        'prescribable_medications': get_prescribable_medications(),
        'suppliers': Supplier.objects.filter(is_active=True).order_by('name'),
        'categories': Category.objects.all().order_by('name'),
        'title': medication.name,
    }
    return render(request, 'pharmacy/item_detail.html', context)

@login_required
def medication_toggle_status(request):
    medication_id = request.POST.get('medication_id')
    if not medication_id:
        messages.error(request, 'Item ID is required.')
        return redirect('pharmacy:medication_list')
    medication = get_object_or_404(Medication, pk=medication_id)
    medication.is_active = not medication.is_active
    medication.save()
    status = 'activated' if medication.is_active else 'deactivated'
    messages.success(request, f'Item "{medication.name}" has been {status}.')
    return redirect('pharmacy:medication_list')

@login_required
def batch_list(request):
    batches = Batch.objects.filter(is_active=True).select_related('medication', 'supplier').order_by('-received_date', 'medication__name')
    low_stock = request.GET.get('low_stock')
    if low_stock:
        batches = batches.filter(quantity_remaining__lte=F('medication__reorder_level'))
    from patients.models import Patient
    return render(request, 'pharmacy/batch_list.html', {
        'batches': batches,
        'low_stock_filter': low_stock,
        'medications': get_sellable_items(),
        'prescribable_medications': get_prescribable_medications(),
        'suppliers': Supplier.objects.filter(is_active=True).order_by('name'),
        'categories': Category.objects.all().order_by('name'),
        'patients': Patient.objects.filter(is_active=True).order_by('first_name'),
    })

@login_required
def batch_create(request):
    initial = {}
    medication_id = request.GET.get('medication')
    if medication_id:
        initial['medication'] = medication_id

    if request.method == 'POST':
        form = BatchForm(request.POST)
        if form.is_valid():
            batch = form.save(commit=False)
            batch.received_by = request.user
            batch.save()
            messages.success(request, f'Batch {batch.batch_number} was created successfully.')
            return redirect('pharmacy:batch_list')
    else:
        form = BatchForm(initial=initial)
    return render(request, 'pharmacy/batch_form.html', {'form': form, 'title': 'Receive New Batch'})

@login_required
def batch_detail(request, pk):
    batch = get_object_or_404(Batch.objects.select_related('medication', 'supplier'), pk=pk)
    return render(request, 'pharmacy/batch_detail.html', {'batch': batch, 'title': f'Batch {batch.batch_number}'})

@login_required
def batch_edit(request, pk):
    batch = get_object_or_404(Batch, pk=pk)
    if request.method == 'POST':
        form = BatchForm(request.POST, instance=batch)
        if form.is_valid():
            batch = form.save()
            messages.success(request, f'Batch {batch.batch_number} was updated successfully.')
            return redirect('pharmacy:batch_list')
    else:
        form = BatchForm(instance=batch)
    return render(request, 'pharmacy/batch_form.html', {'form': form, 'batch': batch, 'title': f'Edit Batch {batch.batch_number}'})

@login_required
@require_POST
def batch_toggle_status(request):
    batch_id = request.POST.get('batch_id')
    if not batch_id:
        messages.error(request, 'Batch ID is required.')
        return redirect('pharmacy:batch_list')
    batch = get_object_or_404(Batch, pk=batch_id)
    batch.is_active = not batch.is_active
    batch.save()
    status = 'activated' if batch.is_active else 'deactivated'
    messages.success(request, f'Batch {batch.batch_number} has been {status}.')
    return redirect('pharmacy:batch_list')

@login_required
def prescription_list(request):
    prescriptions = Prescription.objects.all().select_related('patient', 'prescribed_by', 'medication').prefetch_related('items__medication').order_by('-prescribed_date')
    status_filter = request.GET.get('status')
    if status_filter:
        prescriptions = prescriptions.filter(status=status_filter)
    from patients.models import Patient
    return render(request, 'pharmacy/prescription_list.html', {
        'prescriptions': prescriptions,
        'status_filter': status_filter,
        'medications': get_sellable_items(),
        'prescribable_medications': get_prescribable_medications(),
        'suppliers': Supplier.objects.filter(is_active=True).order_by('name'),
        'categories': Category.objects.all().order_by('name'),
        'patients': Patient.objects.filter(is_active=True).order_by('first_name'),
    })

@login_required
def prescription_create(request):
    if request.method == 'POST':
        form = PrescriptionForm(request.POST)
        if form.is_valid():
            prescription = form.save(commit=False)
            prescription.prescribed_by = request.user
            prescription.save()
            messages.success(request, 'Prescription created successfully.')
            return redirect('pharmacy:prescription_list')
    else:
        form = PrescriptionForm()
    return render(request, 'pharmacy/prescription_form.html', {'form': form, 'title': 'New Prescription'})

def _dispense_prescription_items(prescription, user, notes=''):
    items = list(prescription.items.all())
    if not items and prescription.medication:
        items = [prescription]
    if not items:
        raise ValueError('This prescription has no medications to dispense.')
    with transaction.atomic():
        for item in items:
            medication = item.medication if hasattr(item, 'medication') else prescription.medication
            quantity = item.quantity if hasattr(item, 'quantity') else (prescription.quantity or 0)
            batch = Batch.objects.filter(
                medication=medication,
                is_active=True,
                quantity_remaining__gte=quantity,
                expiry_date__gte=timezone.now().date()
            ).order_by('expiry_date').first()
            if not batch:
                raise ValueError(f'No available stock for {medication.name}.')
            StockMovement.objects.create(
                batch=batch,
                movement_type='out',
                quantity=quantity,
                reference=f'PRESCRIPTION-{prescription.id}',
                notes=notes or f'Dispensed from prescription {prescription.id}',
                created_by=user
            )
        prescription.status = 'dispensed'
        prescription.dispensed_by = user
        prescription.dispensed_date = timezone.now()
        prescription.save()
    return prescription

@login_required
def dispense_prescription(request, pk=None):
    if pk is None:
        messages.error(request, 'Prescription ID is required.')
        return redirect('pharmacy:prescription_list')
    prescription = get_object_or_404(Prescription.objects.select_related('patient', 'prescribed_by', 'medication').prefetch_related('items__medication'), pk=pk)
    if request.method == 'POST':
        try:
            _dispense_prescription_items(prescription, request.user, request.POST.get('dispensed_notes', ''))
            messages.success(request, 'Prescription dispensed successfully.')
            return redirect('pharmacy:prescription_list')
        except ValueError as exc:
            messages.error(request, str(exc))
    return render(request, 'pharmacy/dispense_prescription.html', {'prescription': prescription})

@login_required
def sales_dashboard(request):
    from django.db.models import Count
    from patients.models import Patient

    sales = StockMovement.objects.filter(
        movement_type='out',
        reference__icontains='SALE'
    ).select_related('batch__medication', 'created_by').annotate(
        revenue=ExpressionWrapper(F('quantity') * F('batch__selling_price'), output_field=DecimalField(max_digits=12, decimal_places=2))
    ).order_by('-created_at')
    today = timezone.now().date()
    week_start = today - timedelta(days=7)
    month_start = today.replace(day=1)
    return render(request, 'pharmacy/sales_dashboard.html', {
        'total_sales': sales.count(),
        'today_sales': sales.filter(created_at__date=today).count(),
        'week_sales': sales.filter(created_at__date__gte=week_start).count(),
        'month_sales': sales.filter(created_at__date__gte=month_start).count(),
        'total_revenue': sales.aggregate(total=Sum('revenue'))['total'] or 0,
        'today_revenue': sales.filter(created_at__date=today).aggregate(total=Sum('revenue'))['total'] or 0,
        'week_revenue': sales.filter(created_at__date__gte=week_start).aggregate(total=Sum('revenue'))['total'] or 0,
        'month_revenue': sales.filter(created_at__date__gte=month_start).aggregate(total=Sum('revenue'))['total'] or 0,
        'top_drugs': sales.values('batch__medication__name').annotate(total_quantity=Sum('quantity'), sales_count=Count('id'), total_revenue=Sum('revenue')).order_by('-total_revenue')[:10],
        'recent_sales': sales[:10],
        'available_batches': Batch.objects.filter(is_active=True, quantity_remaining__gt=0, expiry_date__gte=timezone.now().date()).select_related('medication').order_by('medication__name', 'expiry_date'),
        'patients': Patient.objects.filter(is_active=True).order_by('first_name', 'last_name'),
        'pending_prescriptions': Prescription.objects.filter(status='pending').select_related('patient', 'medication').prefetch_related('items__medication').order_by('-prescribed_date')[:20],
    })

@login_required
def sales_list(request):
    sales = StockMovement.objects.filter(
        movement_type='out',
        reference__icontains='SALE'
    ).select_related('batch__medication', 'created_by').order_by('-created_at')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date:
        sales = sales.filter(created_at__date__gte=start_date)
    if end_date:
        sales = sales.filter(created_at__date__lte=end_date)
    return render(request, 'pharmacy/sales_list.html', {'sales': sales, 'start_date': start_date, 'end_date': end_date})

@login_required
def medication_create_ajax(request):
    if request.method != 'POST' or request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return JsonResponse({'error': 'AJAX request required'}, status=400)
    form = MedicationForm(request.POST)
    if form.is_valid():
        medication = form.save()
        return JsonResponse({'success': True, 'message': f'Item "{medication.name}" created successfully!', 'medication_id': medication.id, 'redirect_url': reverse('pharmacy:medication_detail', kwargs={'pk': medication.id})})
    return JsonResponse({'success': False, 'errors': form.errors, 'message': 'Please correct the errors below.'}, status=400)

@login_required
def medication_update_ajax(request, pk):
    if request.method != 'POST' or request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return JsonResponse({'error': 'AJAX request required'}, status=400)
    medication = get_object_or_404(Medication, pk=pk)
    form = MedicationForm(request.POST, instance=medication)
    if form.is_valid():
        medication = form.save()
        return JsonResponse({'success': True, 'message': f'Item "{medication.name}" updated successfully!', 'redirect_url': reverse('pharmacy:medication_detail', kwargs={'pk': medication.id})})
    return JsonResponse({'success': False, 'errors': form.errors, 'message': 'Please correct the errors below.'}, status=400)

@login_required
def batch_create_ajax(request):
    if request.method != 'POST' or request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return JsonResponse({'error': 'AJAX request required'}, status=400)
    form = BatchForm(request.POST)
    if form.is_valid():
        batch = form.save(commit=False)
        batch.received_by = request.user
        batch.save()
        return JsonResponse({'success': True, 'message': f'Batch {batch.batch_number} created successfully!', 'batch_id': batch.id, 'redirect_url': reverse('pharmacy:batch_list')})
    return JsonResponse({'success': False, 'errors': form.errors, 'message': 'Please correct the errors below.'}, status=400)

@login_required
def batch_update_ajax(request, pk):
    if request.method != 'POST' or request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return JsonResponse({'error': 'AJAX request required'}, status=400)
    batch = get_object_or_404(Batch, pk=pk)
    form = BatchForm(request.POST, instance=batch)
    if form.is_valid():
        batch = form.save()
        return JsonResponse({'success': True, 'message': f'Batch {batch.batch_number} updated successfully!', 'redirect_url': reverse('pharmacy:batch_list')})
    return JsonResponse({'success': False, 'errors': form.errors, 'message': 'Please correct the errors below.'}, status=400)

@login_required
def prescription_create_ajax(request):
    if request.method != 'POST' or request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return JsonResponse({'error': 'AJAX request required'}, status=400)
    import json
    from .models import PrescriptionItem
    from patients.models import Patient
    try:
        payload = json.loads(request.body.decode('utf-8'))
        patient = get_object_or_404(Patient, pk=payload.get('patient'))
        medication_rows = payload.get('medications', '[]')
        medication_rows = json.loads(medication_rows) if isinstance(medication_rows, str) else medication_rows
        if not medication_rows:
            return JsonResponse({'success': False, 'message': 'Please add at least one medication.'}, status=400)
        with transaction.atomic():
            prescription = Prescription.objects.create(patient=patient, instructions=payload.get('instructions', ''), prescribed_by=request.user, status='pending')
            for row in medication_rows:
                PrescriptionItem.objects.create(
                    prescription=prescription,
                    medication_id=row['medication'],
                    dosage=row['dosage'],
                    frequency=row['frequency'],
                    duration=row['duration'],
                    quantity=int(row['quantity']),
                    notes=row.get('notes', '')
                )
        return JsonResponse({'success': True, 'message': 'Prescription created successfully.', 'prescription_id': prescription.id, 'redirect_url': reverse('pharmacy:prescription_list')})
    except Exception as exc:
        return JsonResponse({'success': False, 'message': f'Error creating prescription: {exc}'}, status=500)

@login_required
def dispense_prescription_ajax(request, pk):
    if request.method != 'POST' or request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return JsonResponse({'error': 'AJAX request required'}, status=400)
    prescription = get_object_or_404(Prescription.objects.prefetch_related('items__medication'), pk=pk)
    try:
        _dispense_prescription_items(prescription, request.user)
        count = prescription.items.count() or 1
        return JsonResponse({'success': True, 'message': f'Prescription dispensed successfully ({count} medication(s))!', 'redirect_url': reverse('pharmacy:prescription_list')})
    except ValueError as exc:
        return JsonResponse({'success': False, 'message': str(exc)}, status=400)

@login_required
def get_prescription_total_ajax(request, prescription_id):
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return JsonResponse({'error': 'AJAX request required'}, status=400)
    prescription = get_object_or_404(Prescription.objects.prefetch_related('items__medication'), pk=prescription_id)
    items = [(item.medication, item.quantity) for item in prescription.items.all()]
    if not items and prescription.medication:
        items = [(prescription.medication, prescription.quantity or 0)]
    total_amount = 0
    items_breakdown = []
    for medication, quantity in items:
        batch = Batch.objects.filter(medication=medication, is_active=True, quantity_remaining__gte=quantity, expiry_date__gte=timezone.now().date()).order_by('selling_price', 'expiry_date').first()
        unit_price = batch.selling_price if batch else 0
        total = unit_price * quantity if batch else 0
        total_amount += total
        items_breakdown.append({'medication': medication.name, 'quantity': quantity, 'unit_price': float(unit_price) if batch else 0, 'total': float(total) if batch else 0})
    return JsonResponse({'success': True, 'total_amount': float(total_amount), 'items': items_breakdown})

@login_required
def get_pending_prescriptions_ajax(request):
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return JsonResponse({'error': 'AJAX request required'}, status=400)
    medication_id = request.GET.get('medication_id')
    prescriptions = Prescription.objects.filter(status='pending').select_related('patient', 'medication').prefetch_related('items__medication').order_by('-prescribed_date')
    if medication_id:
        prescriptions = prescriptions.filter(Q(medication_id=medication_id) | Q(items__medication_id=medication_id)).distinct()
    data = []
    for prescription in prescriptions:
        data.append({
            'id': prescription.id,
            'patient_id': prescription.patient.id if prescription.patient else None,
            'patient_name': prescription.patient.get_full_name() if prescription.patient else 'Unknown',
            'patient_identifier': prescription.patient.patient_id if prescription.patient else '',
            'medication_id': prescription.medication_id,
            'quantity': prescription.quantity or 0,
            'is_multi': prescription.items.exists(),
        })
    return JsonResponse({'success': True, 'prescriptions': data, 'count': len(data)})

@login_required
def stock_adjustment_ajax(request, batch_id):
    if request.method != 'POST' or request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return JsonResponse({'error': 'AJAX request required'}, status=400)
    batch = get_object_or_404(Batch, pk=batch_id, is_active=True)
    form = StockAdjustmentForm(request.POST)
    if form.is_valid():
        movement = form.save(commit=False)
        movement.batch = batch
        movement.created_by = request.user
        movement.save()
        return JsonResponse({'success': True, 'message': 'Stock adjusted successfully.', 'redirect_url': reverse('pharmacy:batch_list')})
    return JsonResponse({'success': False, 'errors': form.errors, 'message': 'Please correct the errors below.'}, status=400)

@login_required
def supplier_create_ajax(request):
    if request.method != 'POST' or request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return JsonResponse({'error': 'AJAX request required'}, status=400)
    form = SupplierForm(request.POST)
    if form.is_valid():
        supplier = form.save()
        return JsonResponse({'success': True, 'message': f'Supplier {supplier.name} created successfully!', 'redirect_url': reverse('pharmacy:supplier_list')})
    return JsonResponse({'success': False, 'errors': form.errors, 'message': 'Please correct the errors below.'}, status=400)

@login_required
def supplier_update_ajax(request, pk):
    if request.method != 'POST' or request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return JsonResponse({'error': 'AJAX request required'}, status=400)
    supplier = get_object_or_404(Supplier, pk=pk)
    form = SupplierForm(request.POST, instance=supplier)
    if form.is_valid():
        supplier = form.save()
        return JsonResponse({'success': True, 'message': f'Supplier {supplier.name} updated successfully!', 'redirect_url': reverse('pharmacy:supplier_list')})
    return JsonResponse({'success': False, 'errors': form.errors, 'message': 'Please correct the errors below.'}, status=400)
