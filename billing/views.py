from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.http import JsonResponse, HttpResponse
from django.db import transaction
from datetime import date, datetime, timedelta
from .models import Invoice, InvoiceLineItem, Payment, InsuranceClaim, PaymentPlan
from .forms import InvoiceForm, InvoiceLineItemFormSet, PaymentForm, InsuranceClaimForm, PaymentPlanForm
from patients.models import Patient
from appointments.models import Appointment, Service
from clinic_system.pagination_utils import paginate_queryset
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import io
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse

@login_required
def billing_dashboard(request):
    from django.utils import timezone
    from django.db.models import Count
    
    # Calculate key metrics
    today = timezone.now().date()
    current_month = today.replace(day=1)
    
    # Monthly revenue
    monthly_revenue = Payment.objects.filter(
        status='completed', 
        payment_date__gte=current_month
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Outstanding amount (sent + overdue invoices)
    outstanding_amount = Invoice.objects.filter(
        status__in=['sent', 'overdue']
    ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    # Daily payments
    daily_payments = Payment.objects.filter(
        status='completed',
        payment_date=today
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Overdue count
    overdue_count = Invoice.objects.filter(status='overdue').count()
    
    # Combined recent and draft invoices (last 15)
    all_invoices = Invoice.objects.select_related('patient').order_by('-created_at')[:15]
    
    # Payment methods summary for current month
    payment_methods_data = Payment.objects.filter(
        status='completed',
        payment_date__gte=current_month
    ).values('payment_method').annotate(
        total=Sum('amount')
    ).order_by('-total')
    
    # Overdue invoices
    overdue_invoices = Invoice.objects.filter(status='overdue').select_related('patient')[:5]
    
    # Insurance claims summary
    insurance_claims_summary = {
        'pending': InsuranceClaim.objects.filter(status='pending').count(),
        'approved': InsuranceClaim.objects.filter(status='approved').count(),
        'processing': InsuranceClaim.objects.filter(status='processing').count(),
        'denied': InsuranceClaim.objects.filter(status='denied').count(),
    }
    
    # Revenue chart data (last 6 months)
    import json
    revenue_chart_labels = []
    revenue_chart_data = []
    for i in range(5, -1, -1):
        month_date = (current_month - timedelta(days=32*i)).replace(day=1)
        next_month = (month_date + timedelta(days=32)).replace(day=1)
        
        month_revenue = Payment.objects.filter(
            status='completed',
            payment_date__gte=month_date,
            payment_date__lt=next_month
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        revenue_chart_labels.append(month_date.strftime('%b %Y'))
        revenue_chart_data.append(float(month_revenue))
    
    # Active patients for invoice creation
    active_patients = Patient.objects.filter(is_active=True).order_by('first_name', 'last_name')
    
    context = {
        'monthly_revenue': monthly_revenue,
        'outstanding_amount': outstanding_amount,
        'daily_payments': daily_payments,
        'overdue_count': overdue_count,
        'recent_invoices': all_invoices,  # Combined recent and draft
        'payment_methods_data': payment_methods_data,
        'overdue_invoices': overdue_invoices,
        'insurance_claims_summary': insurance_claims_summary,
        'revenue_chart_labels': json.dumps(revenue_chart_labels),
        'revenue_chart_data': json.dumps(revenue_chart_data),
        'active_patients': active_patients,
        'modal_active_patients': active_patients,
    }
    return render(request, 'billing/billing_dashboard.html', context)

@login_required
def invoice_create_for_patient(request):
    """Create a new invoice directly for a selected patient"""
    if request.method == 'POST':
        patient_id = request.POST.get('patient_id')
        if patient_id:
            patient = get_object_or_404(Patient, pk=patient_id)
            
            # Generate invoice number
            last_invoice = Invoice.objects.order_by('-id').first()
            if last_invoice and last_invoice.invoice_number:
                try:
                    last_number = int(last_invoice.invoice_number.split('-')[1])
                    invoice_number = f"INV-{last_number + 1:06d}"
                except (ValueError, IndexError):
                    invoice_count = Invoice.objects.count()
                    invoice_number = f"INV-{invoice_count + 1:06d}"
            else:
                invoice_number = "INV-000001"
            
            # Create draft invoice
            from django.utils import timezone
            due_date = timezone.now().date() + timedelta(days=30)
            
            invoice = Invoice.objects.create(
                invoice_number=invoice_number,
                patient=patient,
                due_date=due_date,
                status='draft',
                subtotal=0,
                tax_rate=0,
                tax_amount=0,
                discount_amount=0,
                total_amount=0,
                notes=f'Invoice created directly for {patient.get_full_name()} on {timezone.now().date()}',
                created_by=request.user,
            )
            
            messages.success(request, f'Draft invoice {invoice_number} created for {patient.get_full_name()}. You can now add services.')
            
            # Handle AJAX request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Draft invoice {invoice_number} created successfully!',
                    'invoice_number': invoice_number,
                    'invoice_id': invoice.pk,
                    'redirect_url': f'/billing/invoices/{invoice.pk}/edit/'
                })
            
            return redirect('billing:invoice_edit', pk=invoice.pk)
        else:
            messages.error(request, 'Please select a patient.')
            
            # Handle AJAX request for error
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'Please select a patient.'
                })
    
    return redirect('billing:billing_dashboard')

@login_required
def invoice_create_ajax(request):
    """AJAX-only endpoint to create a new invoice header via modal.
    Returns JSON and rejects non-AJAX GETs."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    post_data = request.POST.copy()
    if not post_data.get('tax_rate'):
        post_data['tax_rate'] = '0'
    if not post_data.get('discount_amount'):
        post_data['discount_amount'] = '0'
    form = InvoiceForm(post_data)
    if form.is_valid():
        try:
            with transaction.atomic():
                invoice = form.save(commit=False)
                invoice.created_by = request.user

                # Generate invoice number
                last_invoice = Invoice.objects.order_by('-id').first()
                if last_invoice and last_invoice.invoice_number:
                    try:
                        last_number = int(last_invoice.invoice_number.split('-')[1])
                        invoice.invoice_number = f"INV-{last_number + 1:06d}"
                    except (ValueError, IndexError):
                        invoice.invoice_number = f"INV-{Invoice.objects.count() + 1:06d}"
                else:
                    invoice.invoice_number = "INV-000001"

                invoice.subtotal = invoice.subtotal or 0
                invoice.tax_rate = invoice.tax_rate or 0
                invoice.tax_amount = invoice.tax_amount or 0
                invoice.discount_amount = invoice.discount_amount or 0
                invoice.total_amount = invoice.total_amount or 0
                invoice.status = invoice.status or 'draft'

                invoice.save()

                # No line items handled here; follow-up happens on edit page

                # Respond based on request type
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'invoice_id': invoice.pk,
                        'invoice_number': invoice.invoice_number,
                        'redirect_url': "/billing/invoices/"
                    })
                else:
                    return redirect('billing:invoice_edit', pk=invoice.pk)
        except Exception as e:
            return JsonResponse({'success': False, 'errors': {'__all__': [str(e)]}}, status=400)

    # Return validation errors
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)

@login_required
def invoice_create_full_ajax(request):
    """Create invoice header and multiple line items in one AJAX POST."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    post_data = request.POST.copy()
    if not post_data.get('tax_rate'):
        post_data['tax_rate'] = '0'
    if not post_data.get('discount_amount'):
        post_data['discount_amount'] = '0'

    header_form = InvoiceForm(post_data)
    if not header_form.is_valid():
        return JsonResponse({'success': False, 'errors': header_form.errors}, status=400)

    # Parse dynamic line items from fields: items-<idx>-service, description, quantity, unit_price
    items = []
    idx = 0
    while True:
        svc = post_data.get(f'items-{idx}-service')
        desc = post_data.get(f'items-{idx}-description')
        qty = post_data.get(f'items-{idx}-quantity')
        price = post_data.get(f'items-{idx}-unit_price')
        if svc is None and desc is None and qty is None and price is None:
            break
        # Only add if service or description is provided
        if (svc or desc) and qty and price:
            items.append({
                'service': svc,
                'description': desc or '',
                'quantity': qty,
                'unit_price': price,
            })
        idx += 1

    if not items:
        return JsonResponse({'success': False, 'errors': {'__all__': ['Please add at least one line item.']}}, status=400)

    try:
        with transaction.atomic():
            invoice = header_form.save(commit=False)
            invoice.created_by = request.user

            # Generate invoice number
            last_invoice = Invoice.objects.order_by('-id').first()
            if last_invoice and last_invoice.invoice_number:
                try:
                    last_number = int(last_invoice.invoice_number.split('-')[1])
                    invoice.invoice_number = f"INV-{last_number + 1:06d}"
                except (ValueError, IndexError):
                    invoice.invoice_number = f"INV-{Invoice.objects.count() + 1:06d}"
            else:
                invoice.invoice_number = "INV-000001"

            # Ensure numeric defaults
            invoice.subtotal = 0
            invoice.tax_amount = 0
            invoice.total_amount = 0
            if not invoice.status:
                invoice.status = 'draft'
            invoice.save()

            # Create line items
            for it in items:
                service = None
                if it['service']:
                    try:
                        service = Service.objects.get(pk=it['service'])
                    except Service.DoesNotExist:
                        service = None
                InvoiceLineItem.objects.create(
                    invoice=invoice,
                    service=service,
                    description=it['description'],
                    quantity=int(float(it['quantity'])),
                    unit_price=float(it['unit_price'])
                )

            # Calculate totals
            invoice.calculate_totals()

            return JsonResponse({
                'success': True,
                'invoice_id': invoice.pk,
                'invoice_number': invoice.invoice_number,
                'redirect_url': "/billing/invoices/"
            })
    except Exception as e:
        return JsonResponse({'success': False, 'errors': {'__all__': [str(e)]}}, status=400)

@login_required
def invoice_list(request):
    # Get all invoices for statistics (before filtering)
    all_invoices = Invoice.objects.select_related('patient').all()
    
    # Calculate invoice statistics
    from django.db.models import Sum, Count, Q
    from datetime import date
    
    stats = {
        'total_invoices': all_invoices.count(),
        'total_amount': all_invoices.aggregate(total=Sum('total_amount'))['total'] or 0,
        'draft_count': all_invoices.filter(status='draft').count(),
        'sent_count': all_invoices.filter(status='sent').count(),
        'paid_count': all_invoices.filter(status='paid').count(),
        'overdue_count': all_invoices.filter(status='overdue').count(),
        'cancelled_count': all_invoices.filter(status='cancelled').count(),
    }
    
    # Calculate paid and outstanding amounts
    paid_amount = 0
    outstanding_amount = 0
    
    for invoice in all_invoices:
        if invoice.status == 'paid':
            paid_amount += invoice.total_amount
        elif invoice.status in ['sent', 'overdue']:
            balance_due = invoice.get_balance_due()
            outstanding_amount += balance_due
    
    stats['paid_amount'] = paid_amount
    stats['outstanding_amount'] = outstanding_amount
    
    # Now filter invoices for the list display
    invoices = all_invoices
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        invoices = invoices.filter(status=status_filter)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        invoices = invoices.filter(
            Q(invoice_number__icontains=search_query) |
            Q(patient__first_name__icontains=search_query) |
            Q(patient__last_name__icontains=search_query)
        )
    
    # Paginate with dynamic page size
    pagination_data = paginate_queryset(request, invoices, default_page_size=25)
    
    context = {
        'page_obj': pagination_data['page_obj'],
        'invoices': pagination_data['items'],
        'status_choices': Invoice.STATUS_CHOICES,
        'selected_status': status_filter,
        'search_query': search_query,
        'page_size': pagination_data['page_size'],
        'query_string': pagination_data['query_string'],
        'stats': stats,  # Add statistics to context
        # Add individual variables for template compatibility
        'total_amount': stats['total_amount'],
        'total_paid': stats['paid_amount'],
        'total_outstanding': stats['outstanding_amount'],
        # For global invoice/payment modals
        'active_patients': Patient.objects.filter(is_active=True).order_by('first_name', 'last_name'),
        'modal_active_patients': Patient.objects.filter(is_active=True).order_by('first_name', 'last_name'),
        'services': Service.objects.all().order_by('name'),
    }
    return render(request, 'billing/invoice_list.html', context)

@login_required
def invoice_create(request):
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        formset = InvoiceLineItemFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                invoice = form.save(commit=False)
                invoice.created_by = request.user
                
                # Generate invoice number
                last_invoice = Invoice.objects.order_by('-id').first()
                if last_invoice:
                    last_number = int(last_invoice.invoice_number.split('-')[1])
                    invoice.invoice_number = f"INV-{last_number + 1:06d}"
                else:
                    invoice.invoice_number = "INV-000001"
                
                invoice.save()
                
                # Save line items
                formset.instance = invoice
                formset.save()
                
                # Calculate totals
                invoice.calculate_totals()
                
                messages.success(request, f'Invoice {invoice.invoice_number} created successfully!')
                return redirect('billing:invoice_detail', pk=invoice.pk)
    else:
        form = InvoiceForm()
        formset = InvoiceLineItemFormSet()
    
    context = {
        'form': form,
        'formset': formset,
        'services': Service.objects.all(),
    }
    return render(request, 'billing/invoice_create.html', context)

@login_required
def invoice_detail(request, pk):
    invoice = get_object_or_404(
        Invoice.objects.select_related('patient', 'created_by'),
        pk=pk
    )
    line_items = invoice.line_items.select_related('service').all()
    payments = invoice.payments.select_related('processed_by').all()
    
    context = {
        'invoice': invoice,
        'line_items': line_items,
        'payments': payments,
        'today': date.today(),
    }
    return render(request, 'billing/invoice_detail.html', context)

@login_required
def invoice_pdf(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    line_items = invoice.line_items.all()
    payments = invoice.payments.all()
    
    context = {
        'invoice': invoice,
        'line_items': line_items,
        'payments': payments,
    }
    return render(request, 'billing/invoice_pdf.html', context)

@login_required
def invoice_print(request, pk):
    """Print view for a single invoice"""
    from django.utils import timezone
    from clinic_settings.models import ClinicSettings
    
    invoice = get_object_or_404(Invoice, pk=pk)
    clinic_settings = ClinicSettings.get_settings()
    
    context = {
        'invoice': invoice,
        'clinic_settings': clinic_settings,
        'now': timezone.now(),
    }
    
    return render(request, 'billing/invoice_print.html', context)

@login_required
def payment_create(request, invoice_pk=None):
    invoice = None
    if invoice_pk:
        invoice = get_object_or_404(Invoice, pk=invoice_pk)
    elif request.GET.get('invoice'):
        # Handle query parameter case
        invoice = get_object_or_404(Invoice, pk=request.GET.get('invoice'))
    
    # Check if invoice is already fully paid
    if invoice and invoice.status == 'paid':
        messages.warning(request, f'Invoice {invoice.invoice_number} is already fully paid. No additional payment needed.')
        
        # Handle AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'already_paid': True,
                'message': f'Invoice {invoice.invoice_number} is already fully paid.',
                'invoice_number': invoice.invoice_number,
                'total_amount': float(invoice.total_amount),
                'redirect_url': f'/billing/invoices/{invoice.pk}/'
            })
        
        return redirect('billing:invoice_detail', pk=invoice.pk)
    
    if request.method == 'POST':
        # Create a mutable copy of POST data and ensure invoice/patient are set
        post_data = request.POST.copy()
        if invoice:
            post_data['patient'] = str(invoice.patient.pk)
            post_data['invoice'] = str(invoice.pk)
        
        form = PaymentForm(post_data, invoice=invoice)
        if form.is_valid():
            try:
                with transaction.atomic():
                    payment = form.save(commit=False)
                    payment.processed_by = request.user
                    
                    # Generate payment ID
                    last_payment = Payment.objects.order_by('-id').first()
                    if last_payment and last_payment.payment_id:
                        try:
                            last_number = int(last_payment.payment_id.split('-')[1])
                            payment.payment_id = f"PAY-{last_number + 1:06d}"
                        except (ValueError, IndexError):
                            payment_count = Payment.objects.count()
                            payment.payment_id = f"PAY-{payment_count + 1:06d}"
                    else:
                        payment.payment_id = "PAY-000001"
                    
                    payment.save()
                    
                    # Update invoice status if fully paid and invoice exists
                    if payment.invoice:
                        total_payments = payment.invoice.payments.filter(status='completed').aggregate(Sum('amount'))['amount__sum'] or 0
                        if total_payments >= payment.invoice.total_amount:
                            payment.invoice.status = 'paid'
                            payment.invoice.save()
                            messages.success(request, f'Payment {payment.payment_id} recorded successfully! Invoice is now fully paid.')
                        else:
                            remaining = payment.invoice.total_amount - total_payments
                            messages.success(request, f'Payment {payment.payment_id} recorded successfully! Remaining balance: ${remaining:.2f}')
                        
                        # Handle AJAX request for quick payment
                        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                            return JsonResponse({
                                'success': True,
                                'message': f'Payment {payment.payment_id} recorded successfully!',
                                'payment_id': payment.payment_id,
                                'amount': float(payment.amount),
                                'balance_due': float(payment.invoice.get_balance_due()),
                                'invoice_status': payment.invoice.status,
                            })
                        
                        return redirect('billing:invoice_detail', pk=payment.invoice.pk)
                    else:
                        messages.success(request, f'Payment {payment.payment_id} recorded successfully!')
                        return redirect('billing:payment_list')
            except Exception as e:
                messages.error(request, f'Error creating payment: {str(e)}')
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'errors': {'__all__': [str(e)]}
                    })
        else:
            # Add debug information for form errors
            messages.error(request, 'Please correct the errors below.')
            # Handle AJAX form errors
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                })
    else:
        initial_data = {}
        if invoice:
            balance_due = invoice.get_balance_due()
            initial_data['amount'] = balance_due if balance_due > 0 else invoice.total_amount
            initial_data['status'] = 'completed'
        form = PaymentForm(initial=initial_data, invoice=invoice)
    
    context = {
        'form': form,
        'invoice': invoice,
    }
    return render(request, 'billing/payment_create.html', context)

@login_required
def payment_detail(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    
    context = {
        'payment': payment,
    }
    return render(request, 'billing/payment_detail.html', context)

@login_required
def payment_receipt(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    
    context = {
        'payment': payment,
    }
    return render(request, 'billing/payment_receipt.html', context)

@login_required
def payment_list(request):
    payments = Payment.objects.select_related('patient', 'invoice').all()
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        payments = payments.filter(status=status_filter)
    
    # Filter by payment method
    method_filter = request.GET.get('method')
    if method_filter:
        payments = payments.filter(payment_method=method_filter)
    
    # Paginate with dynamic page size
    pagination_data = paginate_queryset(request, payments, default_page_size=25)
    
    context = {
        'page_obj': pagination_data['page_obj'],
        'payments': pagination_data['items'],
        'status_choices': Payment.PAYMENT_STATUS,
        'method_choices': Payment.PAYMENT_METHODS,
        'selected_status': status_filter,
        'selected_method': method_filter,
        'page_size': pagination_data['page_size'],
        'query_string': pagination_data['query_string'],
        # For global payment modal patient selector (dedicated var to avoid conflicts)
        'modal_active_patients': Patient.objects.filter(is_active=True).order_by('first_name', 'last_name'),
    }
    return render(request, 'billing/payment_list.html', context)

@login_required
def insurance_claim_list(request):
    claims = InsuranceClaim.objects.select_related('patient', 'invoice').all()
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        claims = claims.filter(status=status_filter)
    
    # Filter by provider
    provider_filter = request.GET.get('provider')
    if provider_filter:
        claims = claims.filter(insurance_provider__icontains=provider_filter)
    
    # Filter by date range
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        claims = claims.filter(submission_date__gte=date_from)
    if date_to:
        claims = claims.filter(submission_date__lte=date_to)
    
    # Calculate summary statistics
    approved_count = claims.filter(status='approved').count()
    pending_count = claims.filter(status__in=['submitted', 'pending']).count()
    total_claim_amount = claims.aggregate(Sum('claim_amount'))['claim_amount__sum'] or 0
    
    paginator = Paginator(claims, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_choices': InsuranceClaim.CLAIM_STATUS,
        'selected_status': status_filter,
        'approved_count': approved_count,
        'pending_count': pending_count,
        'total_claim_amount': total_claim_amount,
    }
    return render(request, 'billing/insurance_claim_list.html', context)

@login_required
def insurance_claim_create(request, invoice_pk=None):
    invoice = None
    if invoice_pk:
        invoice = get_object_or_404(Invoice, pk=invoice_pk)
    
    if request.method == 'POST':
        form = InsuranceClaimForm(request.POST)
        if form.is_valid():
            claim = form.save(commit=False)
            if invoice:
                claim.invoice = invoice
                claim.patient = invoice.patient
            claim.submitted_by = request.user
            
            # Generate claim number
            last_claim = InsuranceClaim.objects.order_by('-id').first()
            if last_claim:
                last_number = int(last_claim.claim_number.split('-')[1])
                claim.claim_number = f"CLM-{last_number + 1:06d}"
            else:
                claim.claim_number = "CLM-000001"
            
            claim.save()
            messages.success(request, f'Insurance claim {claim.claim_number} submitted successfully!')
            return redirect('billing:insurance_claim_list')
    else:
        initial_data = {}
        if invoice:
            # Pre-populate with patient's insurance information
            initial_data = {
                'insurance_provider': invoice.patient.insurance_provider,
                'policy_number': invoice.patient.insurance_policy_number,
                'group_number': invoice.patient.insurance_group_number,
                'claim_amount': invoice.total_amount,
            }
        form = InsuranceClaimForm(initial=initial_data)
    
    context = {
        'form': form,
        'invoice': invoice,
    }
    return render(request, 'billing/insurance_claim_create.html', context)

@login_required
def insurance_claim_print(request, pk):
    """Print view for insurance claim"""
    from clinic_settings.models import ClinicSettings
    
    claim = get_object_or_404(InsuranceClaim, pk=pk)
    
    # Get clinic settings for logo
    try:
        clinic_settings = ClinicSettings.objects.first()
    except:
        clinic_settings = None
    
    context = {
        'claim': claim,
        'patient': claim.patient,
        'invoice': claim.invoice,
        'clinic_settings': clinic_settings,
    }
    return render(request, 'billing/insurance_claim_print.html', context)

@login_required
def payment_plan_list(request):
    payment_plans = PaymentPlan.objects.select_related('patient', 'invoice').all()
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        payment_plans = payment_plans.filter(status=status_filter)
    
    paginator = Paginator(payment_plans, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_choices': PaymentPlan.PLAN_STATUS,
        'selected_status': status_filter,
    }
    return render(request, 'billing/payment_plan_list.html', context)

@login_required
def payment_plan_create(request, invoice_pk):
    invoice = get_object_or_404(Invoice, pk=invoice_pk)
    
    if request.method == 'POST':
        form = PaymentPlanForm(request.POST)
        if form.is_valid():
            payment_plan = form.save(commit=False)
            payment_plan.invoice = invoice
            payment_plan.patient = invoice.patient
            payment_plan.created_by = request.user
            
            # Generate payment plan ID
            last_plan = PaymentPlan.objects.order_by('-id').first()
            if last_plan:
                last_number = int(last_plan.plan_id.split('-')[1])
                payment_plan.plan_id = f"PP-{last_number + 1:06d}"
            else:
                payment_plan.plan_id = "PP-000001"
            
            payment_plan.save()
            messages.success(request, f'Payment plan {payment_plan.plan_id} created successfully!')
            return redirect('billing:payment_plan_detail', pk=payment_plan.pk)
    else:
        form = PaymentPlanForm(initial={'total_amount': invoice.total_amount})
    
    context = {
        'form': form,
        'invoice': invoice,
    }
    return render(request, 'billing/payment_plan_create.html', context)

@login_required
def payment_plan_detail(request, pk):
    payment_plan = get_object_or_404(PaymentPlan, pk=pk)
    
    context = {
        'payment_plan': payment_plan,
    }
    return render(request, 'billing/payment_plan_detail.html', context)

@login_required
def invoice_status_update(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Invoice.STATUS_CHOICES):
            invoice.status = new_status
            invoice.save()
            messages.success(request, f'Invoice status updated to {invoice.get_status_display()}')
        else:
            messages.error(request, 'Invalid status selected')
    
    return redirect('billing:invoice_detail', pk=pk)

@login_required
def bulk_invoice_action(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        invoice_ids = request.POST.getlist('invoice_ids')
        
        if not invoice_ids:
            messages.error(request, 'No invoices selected')
            return redirect('billing:invoice_list')
        
        invoices = Invoice.objects.filter(id__in=invoice_ids)
        
        if action == 'mark_sent':
            invoices.update(status='sent')
            messages.success(request, f'{len(invoice_ids)} invoices marked as sent')
        elif action == 'mark_paid':
            invoices.update(status='paid')
            messages.success(request, f'{len(invoice_ids)} invoices marked as paid')
        elif action == 'mark_overdue':
            invoices.update(status='overdue')
            messages.success(request, f'{len(invoice_ids)} invoices marked as overdue')
        else:
            messages.error(request, 'Invalid action selected')
    
    return redirect('billing:invoice_list')

@login_required
def payment_receipt_pdf(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    
    # Create PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Header
    title = Paragraph(f"PAYMENT RECEIPT", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 12))
    
    # Receipt details
    receipt_data = [
        ['Payment ID:', payment.payment_id],
        ['Payment Date:', payment.payment_date.strftime('%Y-%m-%d %H:%M')],
        ['Amount:', f"${payment.amount}"],
        ['Method:', payment.get_payment_method_display()],
        ['Status:', payment.get_status_display()],
    ]
    
    if payment.reference_number:
        receipt_data.append(['Reference:', payment.reference_number])
    
    receipt_table = Table(receipt_data, colWidths=[2*72, 3*72])
    receipt_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
    ]))
    story.append(receipt_table)
    story.append(Spacer(1, 12))
    
    # Patient and invoice information
    patient_info = Paragraph(f"<b>Patient:</b><br/>{payment.patient.get_full_name()}<br/><b>Invoice:</b> {payment.invoice.invoice_number}", styles['Normal'])
    story.append(patient_info)
    
    doc.build(story)
    buffer.seek(0)
    
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="receipt_{payment.payment_id}.pdf"'
    return response

@login_required
def send_payment_receipt_email(request, pk):
    """Send payment receipt via email"""
    payment = get_object_or_404(Payment, pk=pk)
    
    if not payment.patient.email:
        return JsonResponse({'success': False, 'error': 'Patient has no email address'})
    
    try:
        # Build absolute link to the receipt PDF
        pdf_link = request.build_absolute_uri(
            reverse('billing:payment_receipt_pdf', kwargs={'pk': payment.pk})
        )

        # Prepare email body with link
        clinic_name = getattr(settings, 'CLINIC_NAME', 'PhysioNutrition Clinic')
        subject = f"Payment Receipt #{payment.payment_id} from {clinic_name}"
        message = render_to_string('billing/email/payment_receipt_email.txt', {
            'payment': payment,
            'clinic_name': clinic_name,
            'pdf_link': pdf_link,
        })

        email = EmailMessage(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [payment.patient.email],
        )
        email.send()
        
        return JsonResponse({'success': True, 'message': f'Receipt sent to {payment.patient.email}'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def invoice_aging_report(request):
    # Calculate aging buckets
    today = date.today()
    
    current_invoices = Invoice.objects.filter(
        status__in=['sent', 'overdue'],
        due_date__gte=today
    )
    
    overdue_1_30 = Invoice.objects.filter(
        status__in=['sent', 'overdue'],
        due_date__lt=today,
        due_date__gte=today - timedelta(days=30)
    )
    
    overdue_31_60 = Invoice.objects.filter(
        status__in=['sent', 'overdue'],
        due_date__lt=today - timedelta(days=30),
        due_date__gte=today - timedelta(days=60)
    )
    
    overdue_61_90 = Invoice.objects.filter(
        status__in=['sent', 'overdue'],
        due_date__lt=today - timedelta(days=60),
        due_date__gte=today - timedelta(days=90)
    )
    
    overdue_90_plus = Invoice.objects.filter(
        status__in=['sent', 'overdue'],
        due_date__lt=today - timedelta(days=90)
    )
    
    context = {
        'current_invoices': current_invoices,
        'overdue_1_30': overdue_1_30,
        'overdue_31_60': overdue_31_60,
        'overdue_61_90': overdue_61_90,
        'overdue_90_plus': overdue_90_plus,
        'current_total': current_invoices.aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
        'overdue_1_30_total': overdue_1_30.aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
        'overdue_31_60_total': overdue_31_60.aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
        'overdue_61_90_total': overdue_61_90.aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
        'overdue_90_plus_total': overdue_90_plus.aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
    }
    return render(request, 'billing/invoice_aging_report.html', context)

@login_required
def get_service_price(request):
    """AJAX endpoint to get service price"""
    service_id = request.GET.get('service_id')
    if service_id:
        try:
            service = Service.objects.get(id=service_id)
            return JsonResponse({
                'price': float(service.price),
                'description': service.name
            })
        except Service.DoesNotExist:
            pass
    
    return JsonResponse({'price': 0, 'description': ''})

@login_required
def payment_debug(request):
    """Debug view to test payment creation"""
    from django.http import HttpResponse
    import json
    
    debug_info = {
        'user': str(request.user),
        'user_authenticated': request.user.is_authenticated,
        'payment_count': Payment.objects.count(),
        'invoice_count': Invoice.objects.count(),
        'patient_count': Patient.objects.count(),
        'available_invoices': list(Invoice.objects.filter(status__in=['draft', 'sent', 'overdue']).values('id', 'invoice_number', 'status')),
        'recent_payments': list(Payment.objects.order_by('-id')[:5].values('payment_id', 'amount', 'status')),
    }
    
    return HttpResponse(json.dumps(debug_info, indent=2), content_type='application/json')

@login_required
def payment_test(request):
    """Test view for payment creation debugging"""
    context = {
        'patients': Patient.objects.filter(is_active=True)[:10],
        'invoices': Invoice.objects.filter(status__in=['draft', 'sent', 'overdue'])[:10],
        'payments': Payment.objects.order_by('-id')[:5],
    }
    return render(request, 'billing/payment_test.html', context)

@login_required
def invoice_edit(request, pk):
    """Edit an existing invoice (especially useful for draft invoices)"""
    invoice = get_object_or_404(Invoice, pk=pk)
    
    if request.method == 'POST':
        form = InvoiceForm(request.POST, instance=invoice)
        formset = InvoiceLineItemFormSet(request.POST, instance=invoice)
        
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                invoice = form.save()
                formset.save()
                
                # Calculate totals
                invoice.calculate_totals()
                
                messages.success(request, f'Invoice {invoice.invoice_number} updated successfully!')
                return redirect('billing:invoice_detail', pk=invoice.pk)
    else:
        form = InvoiceForm(instance=invoice)
        formset = InvoiceLineItemFormSet(instance=invoice)
    
    context = {
        'form': form,
        'formset': formset,
        'invoice': invoice,
        'services': Service.objects.all(),
        'is_edit': True,
    }
    return render(request, 'billing/invoice_create.html', context)

@login_required
def patient_draft_invoices(request, patient_id):
    """View draft invoices for a specific patient"""
    patient = get_object_or_404(Patient, patient_id=patient_id)
    draft_invoices = Invoice.objects.filter(patient=patient, status='draft').order_by('-created_at')
    
    context = {
        'patient': patient,
        'draft_invoices': draft_invoices,
    }
    return render(request, 'billing/patient_draft_invoices.html', context)

@login_required
def send_invoice_email(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    
    if not invoice.patient.email:
        return JsonResponse({'success': False, 'error': 'Patient has no email address'})
    
    try:
        # Build absolute link to the printable invoice page (can be saved as PDF by recipient)
        pdf_link = request.build_absolute_uri(
            reverse('billing:invoice_pdf', kwargs={'pk': invoice.pk})
        )

        # Prepare email body with link
        clinic_name = getattr(settings, 'CLINIC_NAME', 'PhysioNutrition Clinic')
        subject = f"Invoice #{invoice.invoice_number} from {clinic_name}"
        message = render_to_string('billing/email/invoice_email.txt', {
            'invoice': invoice,
            'clinic_name': clinic_name,
            'pdf_link': pdf_link,
        })

        email = EmailMessage(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [invoice.patient.email],
        )
        email.send()
        
        # Update invoice status
        invoice.status = 'sent'
        invoice.save()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# ==================== AJAX-ONLY VIEWS ====================

@login_required
def payment_record_ajax(request):
    """AJAX-only payment recording view"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    # Accept both AJAX and regular form POSTs
    
    # Get invoice if provided
    invoice = None
    invoice_pk = request.POST.get('invoice') or request.GET.get('invoice')
    if invoice_pk:
        try:
            invoice = get_object_or_404(Invoice, pk=invoice_pk)
            
            # Check if invoice is already fully paid
            if invoice.status == 'paid':
                return JsonResponse({
                    'success': False,
                    'already_paid': True,
                    'message': f'Invoice {invoice.invoice_number} is already fully paid.',
                    'invoice_number': invoice.invoice_number,
                    'total_amount': float(invoice.total_amount),
                    'redirect_url': f'/billing/invoices/{invoice.pk}/'
                }, status=400)
        except:
            pass
    
    # Create a mutable copy of POST data
    post_data = request.POST.copy()
    
    # Debug logging
    import logging
    logger = logging.getLogger(__name__)
    logger.error(f"RAW POST DATA: {dict(request.POST)}")
    logger.error(f"Invoice param: {invoice}")
    
    if invoice:
        post_data['patient'] = str(invoice.patient.pk)
        post_data['invoice'] = str(invoice.pk)
    else:
        # Handle empty string for invoice - convert to None/remove field
        if 'invoice' in post_data and not post_data.get('invoice'):
            logger.error(f"Removing empty invoice field. Value was: '{post_data.get('invoice')}'")
            del post_data['invoice']
    
    logger.error(f"CLEANED POST DATA: {dict(post_data)}")
    
    form = PaymentForm(post_data, invoice=invoice)
    if form.is_valid():
        try:
            with transaction.atomic():
                payment = form.save(commit=False)
                payment.processed_by = request.user
                
                # Force invoice to None if it's empty (critical for NULL constraint)
                logger.error(f"BEFORE FIX - payment.invoice: {payment.invoice}, payment.invoice_id: {payment.invoice_id}")
                if not payment.invoice or payment.invoice == '' or payment.invoice_id == '':
                    payment.invoice = None
                    payment.invoice_id = None
                logger.error(f"AFTER FIX - payment.invoice: {payment.invoice}, payment.invoice_id: {payment.invoice_id}")
                
                # Generate payment ID
                last_payment = Payment.objects.order_by('-id').first()
                if last_payment and last_payment.payment_id:
                    try:
                        last_number = int(last_payment.payment_id.split('-')[1])
                        payment.payment_id = f"PAY-{last_number + 1:06d}"
                    except (ValueError, IndexError):
                        payment_count = Payment.objects.count()
                        payment.payment_id = f"PAY-{payment_count + 1:06d}"
                else:
                    payment.payment_id = "PAY-000001"
                
                logger.error(f"ABOUT TO SAVE - invoice: {payment.invoice}, invoice_id: {payment.invoice_id}")
                payment.save()
                logger.error(f"SAVE SUCCESSFUL!")
                
                # Update invoice status if fully paid and invoice exists
                if payment.invoice:
                    total_payments = payment.invoice.payments.filter(status='completed').aggregate(Sum('amount'))['amount__sum'] or 0
                    if total_payments >= payment.invoice.total_amount:
                        payment.invoice.status = 'paid'
                        payment.invoice.save()
                        message = f'Payment {payment.payment_id} recorded successfully! Invoice is now fully paid.'
                    else:
                        remaining = payment.invoice.total_amount - total_payments
                        message = f'Payment {payment.payment_id} recorded successfully! Remaining balance: UGX {remaining:,.0f}'
                    
                    from django.urls import reverse
                    # If AJAX, return JSON; otherwise redirect
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'success': True,
                            'message': message,
                            'payment_id': payment.payment_id,
                            'amount': float(payment.amount),
                            'balance_due': float(payment.invoice.get_balance_due()),
                            'invoice_status': payment.invoice.status,
                            'redirect_url': reverse('billing:invoice_detail', kwargs={'pk': payment.invoice.pk})
                        })
                    else:
                        return redirect('billing:invoice_detail', pk=payment.invoice.pk)
                else:
                    from django.urls import reverse
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'success': True,
                            'message': f'Payment {payment.payment_id} recorded successfully!',
                            'payment_id': payment.payment_id,
                            'amount': float(payment.amount),
                            'redirect_url': reverse('billing:payment_list')
                        })
                    else:
                        return redirect('billing:payment_list')
        except Exception as e:
            return JsonResponse({
                'success': False,
                'errors': {'__all__': [str(e)]},
                'message': f'Error creating payment: {str(e)}'
            }, status=400)
    else:
        # Return form errors for client-side display
        logger.error(f"❌ FORM VALIDATION FAILED!")
        logger.error(f"Form errors: {form.errors}")
        logger.error(f"Form errors as dict: {form.errors.as_data()}")
        logger.error(f"Non-field errors: {form.non_field_errors()}")
        
        errors = {}
        for field, error_list in form.errors.items():
            errors[field] = [str(e) for e in error_list]  # Convert to strings
        
        return JsonResponse({
            'success': False,
            'errors': errors,
            'message': 'Please correct the errors below and try again.',
            'form_errors': str(form.errors)  # Add raw form errors for debugging
        }, status=400)

@login_required
def invoices_for_patient_ajax(request):
    """Return a list of open (unpaid) invoices for a given patient (by pk)."""
    import logging
    logger = logging.getLogger(__name__)
    
    logger.error(f"🔍 INVOICE FETCH - Method: {request.method}")
    logger.error(f"🔍 INVOICE FETCH - GET params: {dict(request.GET)}")
    
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    patient_id = request.GET.get('patient')
    logger.error(f"🔍 INVOICE FETCH - Patient ID: {patient_id}")
    
    if not patient_id:
        return JsonResponse({'error': 'Missing patient parameter'}, status=400)
    try:
        patient = Patient.objects.get(pk=patient_id)
        logger.error(f"🔍 INVOICE FETCH - Patient found: {patient.get_full_name()}")
    except Patient.DoesNotExist:
        logger.error(f"🔍 INVOICE FETCH - Patient NOT found!")
        return JsonResponse({'error': 'Patient not found'}, status=404)

    # Consider invoices not fully paid
    invoices_qs = Invoice.objects.filter(patient=patient).exclude(status='paid').order_by('-created_at')
    logger.error(f"🔍 INVOICE FETCH - Total invoices found: {invoices_qs.count()}")

    data = []
    for inv in invoices_qs[:50]:
        try:
            balance = float(inv.get_balance_due()) if hasattr(inv, 'get_balance_due') else float(inv.total_amount)
        except Exception:
            balance = float(inv.total_amount)
        
        logger.error(f"🔍 INVOICE {inv.invoice_number} - Balance: {balance}")
        
        # Only include invoices with outstanding balance
        if balance > 0:
            data.append({
                'id': inv.pk,
                'invoice_number': getattr(inv, 'invoice_number', f'INV-{inv.pk}'),
                'status': inv.status,
                'total_amount': float(inv.total_amount),
                'balance_due': balance,
                'created_at': inv.created_at.isoformat() if hasattr(inv, 'created_at') else None,
            })

    logger.error(f"🔍 INVOICE FETCH - Returning {len(data)} unpaid invoices")
    return JsonResponse({'success': True, 'invoices': data})
