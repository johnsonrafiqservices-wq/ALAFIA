import os
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
from datetime import datetime, time, timedelta
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Min, Max
from django.http import JsonResponse, HttpResponse
from django.core.files.base import ContentFile
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods
from .models import Patient, VitalSigns, Triage, Assessment, TriageAssessment, BirthdayWish, PhysiotherapyClinicalReasoningForm
from datetime import date as date_cls
from .forms import PatientForm, VisitingPatientForm, VitalSignsForm, TriageForm, AssessmentForm, PhysiotherapyAssessmentForm, NutritionAssessmentForm, TriageAssessmentForm, AssessmentUpdateForm
from appointments.models import Appointment, Service
from medical_records.decorators import medical_staff_required
from clinic_settings.models import ClinicSettings
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.urls import reverse_lazy
from clinic_system.pagination_utils import paginate_queryset

def generate_barcode_base64(patient_id):
    """Generate a barcode image and return as base64"""
    try:
        code128 = barcode.get_barcode_class('code128')
        barcode_instance = code128(patient_id, writer=ImageWriter())
        buffer = BytesIO()
        barcode_instance.write(buffer, {
            'write_text': False,
            'quiet_zone': 2,
            'module_height': 6,
            'module_width': 0.2,
        })
        import base64
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
    except Exception as e:
        print(f"Error generating barcode: {e}")
        return None

@login_required
def dashboard(request):
    # Get active tab from URL or default to 'overview'
    active_tab = request.GET.get('tab', 'overview')
    
    # Dashboard statistics - Show all patients for all user roles
    total_patients = Patient.objects.filter(is_active=True).count()
    recent_patients = Patient.objects.filter(is_active=True).order_by('-registration_date')[:10]
    pending_triage = Triage.objects.filter(priority_level__in=['1', '2']).order_by('-triage_date')[:5]
    
    # Today's birthdays
    today = date_cls.today()
    birthday_patients = Patient.objects.filter(
        date_of_birth__month=today.month,
        date_of_birth__day=today.day,
        is_active=True,
    )
    
    # Add barcode data to recent patients
    for patient in recent_patients:
        patient.barcode_data = generate_barcode_base64(patient.patient_id)

    # ── Return / retention statistics for dashboard ────────────────
    from django.db.models import Count, Min, Max
    from datetime import timedelta

    # New patients this month
    month_start = today.replace(day=1)
    new_this_month = Patient.objects.filter(
        is_active=True,
        registration_date__date__gte=month_start
    ).count()

    # Returning patients = those with more than 1 assessment
    returning_count = Patient.objects.filter(is_active=True).annotate(
        vc=Count('assessments')
    ).filter(vc__gt=1).count()

    # Return rate (returning / total active with at least 1 visit)
    visited_count = Patient.objects.filter(
        is_active=True, assessments__isnull=False
    ).distinct().count()
    return_rate_dashboard = round(returning_count / visited_count * 100) if visited_count > 0 else 0

    # Patients who haven't visited in 30+ days (at-risk / lapsed)
    thirty_days_ago = today - timedelta(days=30)
    lapsed_patients = Patient.objects.filter(is_active=True).annotate(
        last_assessment=Max('assessments__assessment_date')
    ).filter(
        last_assessment__date__lt=thirty_days_ago
    ).count()

    # Top 5 most frequent returning patients
    top_returning_dashboard = Patient.objects.filter(is_active=True).annotate(
        visit_count=Count('assessments')
    ).filter(visit_count__gt=1).order_by('-visit_count')[:5]

    # Today's appointments
    today_appointments_count = Appointment.objects.filter(appointment_date=today).count()

    context = {
        'total_patients': total_patients,
        'recent_patients': recent_patients,
        'pending_triage': pending_triage,
        'user_role': request.user.role,
        'active_tab': active_tab,
        'birthday_patients': birthday_patients,
        'today': today,
        # Return stats
        'new_this_month': new_this_month,
        'returning_count': returning_count,
        'return_rate_dashboard': return_rate_dashboard,
        'lapsed_patients': lapsed_patients,
        'top_returning_dashboard': top_returning_dashboard,
        'today_appointments_count': today_appointments_count,
    }
    return render(request, 'dashboard/dashboard.html', context)

@login_required
def patient_list(request):
    # Show all active patients for all user roles
    patients = Patient.objects.filter(is_active=True)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        patients = patients.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(patient_id__icontains=search_query) |
            Q(phone__icontains=search_query)
        )
    
    # Paginate with dynamic page size
    pagination_data = paginate_queryset(request, patients, default_page_size=25)
    
    context = {
        'page_obj': pagination_data['page_obj'],
        'patients': pagination_data['items'],
        'search_query': search_query,
        'user_role': request.user.role,
        'page_size': pagination_data['page_size'],
        'query_string': pagination_data['query_string'],
    }
    return render(request, 'patients/patient_list.html', context)

def generate_barcode(patient_id):
    """Generate a barcode image for the patient ID"""
    # Create a Code128 barcode
    code128 = barcode.get_barcode_class('code128')
    
    # Generate the barcode
    barcode_instance = code128(patient_id, writer=ImageWriter())
    
    # Create a BytesIO buffer to save the image
    buffer = BytesIO()
    
    # Write the barcode to the buffer
    barcode_instance.write(buffer, {
        'write_text': False,  # Don't write the text below the barcode
        'quiet_zone': 2,      # Add some padding around the barcode
        'module_height': 6,   # Height of the barcode
        'module_width': 0.2,  # Width of the thinnest bar
    })
    
    # Convert to base64 for embedding in HTML
    import base64
    barcode_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return f'data:image/png;base64,{barcode_base64}'

@login_required
def patient_detail(request, patient_id):
    patient = get_object_or_404(Patient, patient_id=patient_id, is_active=True)
    
    # Get vital signs (last 10 records)
    vital_signs = VitalSigns.objects.filter(patient=patient).select_related('recorded_by').order_by('-recorded_date')[:10]
    
    # Get recent appointments (last 5 upcoming or recent)
    try:
        from appointments.models import Appointment, Service
        appointments = Appointment.objects.filter(patient=patient).select_related('provider', 'service')\
            .order_by('-appointment_date', '-appointment_time')[:5]
        # Get active services for appointment scheduling
        services = Service.objects.filter(is_active=True).order_by('category', 'name')
    except ImportError:
        appointments = []
        services = []
    
    # Get recent documents (last 5)
    try:
        from medical_records.models import Document
        documents = Document.objects.filter(patient=patient).order_by('-uploaded_at')[:5]
    except ImportError:
        documents = []
    
    # Get triage records (last 5)
    triages = Triage.objects.filter(patient=patient)\
        .select_related('triaged_by').order_by('-triage_date')[:5]
    
    # Get assessments (last 5) - filtered by user role
    assessments_query = Assessment.objects.filter(patient=patient).select_related('assessed_by')
    
    # Role-based filtering for assessments
    if request.user.role == 'physiotherapist':
        # Physiotherapists can only see physiotherapy assessments
        assessments = assessments_query.filter(department='physiotherapy').order_by('-assessment_date')[:5]
    elif request.user.role == 'nutritionist':
        # Nutritionists can only see nutrition assessments
        assessments = assessments_query.filter(department='nutrition').order_by('-assessment_date')[:5]
    else:
        # Doctors, admins, nurses can see all assessments
        assessments = assessments_query.order_by('-assessment_date')[:5]
    
    # Get billing information (invoices)
    try:
        from billing.models import Invoice
        invoices = Invoice.objects.filter(patient=patient).order_by('-issue_date')[:5]
        # Get draft invoices separately for easy access
        draft_invoices = Invoice.objects.filter(patient=patient, status='draft').order_by('-created_at')
    except ImportError:
        invoices = []
        draft_invoices = []
    
    # Generate barcode for the patient
    barcode_data = generate_barcode(patient.patient_id)
    
    # Calculate outstanding totals
    invoices_total = invoices.aggregate(total=Sum('total_amount'))['total'] if invoices else 0
    total_due = invoices_total or 0

    # Get clinic settings for header
    try:
        clinic_settings = ClinicSettings.objects.first()
    except:
        clinic_settings = None
    
    # Get medical staff for appointment providers
    User = get_user_model()
    providers = User.objects.filter(
        is_active=True,
        role__in=['doctor', 'physiotherapist', 'nutritionist']
    ).order_by('first_name', 'last_name')
    
    # Laboratory Results for this patient
    from laboratory.models import LabTestResult
    lab_results = LabTestResult.objects.filter(request__patient=patient).select_related('request__test').order_by('-date_reported')

    # Assessment Prescriptions for this patient (assuming prescriptions are stored in Assessment model's treatment_plan or a related model)
    # If you have a separate Prescription model, replace this logic accordingly
    assessment_prescriptions = []
    for assessment in assessments:
        if hasattr(assessment, 'treatment_plan') and assessment.treatment_plan:
            assessment_prescriptions.append({
                'date': assessment.assessment_date,
                'prescribed_by': assessment.assessed_by,
                'text': assessment.treatment_plan,
            })
    
    # Get medications from pharmacy for prescription modal
    try:
        from pharmacy.models import Medication, Prescription
        medications = Medication.objects.filter(is_active=True).order_by('name')
        # Get actual prescriptions for this patient
        prescriptions = Prescription.objects.filter(patient=patient).select_related(
            'medication', 'prescribed_by', 'dispensed_by'
        ).order_by('-prescribed_date')[:10]
    except ImportError:
        medications = []
        prescriptions = []

    # ── Patient visit / return statistics ──────────────────────────
    from datetime import date as _date

    all_assessments = Assessment.objects.filter(patient=patient).order_by('assessment_date')
    total_visits = all_assessments.count()
    first_visit_date = None
    last_visit_date = None
    days_since_last_visit = None
    avg_days_between_visits = None
    visit_frequency_label = 'No visits'

    if total_visits > 0:
        agg = all_assessments.aggregate(first=Min('assessment_date'), last=Max('assessment_date'))
        first_visit_date = agg['first'].date() if agg['first'] else None
        last_visit_date  = agg['last'].date()  if agg['last']  else None
        if last_visit_date:
            days_since_last_visit = (_date.today() - last_visit_date).days
        if total_visits > 1 and first_visit_date and last_visit_date:
            span = (last_visit_date - first_visit_date).days
            avg_days_between_visits = round(span / (total_visits - 1))
            if avg_days_between_visits <= 7:
                visit_frequency_label = 'Weekly'
            elif avg_days_between_visits <= 14:
                visit_frequency_label = 'Bi-weekly'
            elif avg_days_between_visits <= 31:
                visit_frequency_label = 'Monthly'
            elif avg_days_between_visits <= 90:
                visit_frequency_label = 'Quarterly'
            else:
                visit_frequency_label = 'Infrequent'
        elif total_visits == 1:
            visit_frequency_label = 'First visit only'

    # Appointments total for this patient
    try:
        from appointments.models import Appointment as _Appt
        total_appt_count = _Appt.objects.filter(patient=patient).count()
        completed_appt_count = _Appt.objects.filter(patient=patient, status='completed').count()
    except Exception:
        total_appt_count = 0
        completed_appt_count = 0

    # Visit trend: counts per month for last 12 months
    from calendar import monthrange as _mr
    visit_trend_labels = []
    visit_trend_data = []
    today_d = _date.today()
    for i in range(11, -1, -1):
        m = today_d.month - i
        y = today_d.year
        while m <= 0:
            m += 12
            y -= 1
        _, ml = _mr(y, m)
        ms = _date(y, m, 1)
        me = _date(y, m, ml)
        cnt = Assessment.objects.filter(
            patient=patient,
            assessment_date__date__range=[ms, me]
        ).count()
        visit_trend_labels.append(ms.strftime('%b'))
        visit_trend_data.append(cnt)

    import json as _json
    visit_trend_labels_json = _json.dumps(visit_trend_labels)
    visit_trend_data_json   = _json.dumps(visit_trend_data)

    context = {
        'patient': patient,
        'vital_signs': vital_signs,
        'triages': triages,
        'assessments': assessments,
        'appointments': appointments,
        'documents': documents,
        'invoices': invoices,
        'draft_invoices': draft_invoices,
        'barcode_data': barcode_data,
        'active_tab': 'overview',
        'lab_results': lab_results,
        'assessment_prescriptions': assessment_prescriptions,
        'clinic_settings': clinic_settings,
        'services': services,
        'providers': providers,
        'medications': medications,
        'prescriptions': prescriptions,
        # Visit / return statistics
        'total_visits': total_visits,
        'first_visit_date': first_visit_date,
        'last_visit_date': last_visit_date,
        'days_since_last_visit': days_since_last_visit,
        'avg_days_between_visits': avg_days_between_visits,
        'visit_frequency_label': visit_frequency_label,
        'total_appt_count': total_appt_count,
        'completed_appt_count': completed_appt_count,
        'visit_trend_labels': visit_trend_labels_json,
        'visit_trend_data': visit_trend_data_json,
    }
    return render(request, 'patients/patient_detail_new.html', context)


@medical_staff_required
def assessment_update(request, patient_id, assessment_id):
    patient = get_object_or_404(Patient, patient_id=patient_id)
    assessment = get_object_or_404(Assessment, pk=assessment_id, patient=patient)

    if request.method == 'POST':
        form = AssessmentUpdateForm(request.POST, instance=assessment)
        if form.is_valid():
            form.save()
            return JsonResponse({
                'success': True,
                'message': 'Assessment updated successfully.',
            })
        status = 400
    else:
        form = AssessmentUpdateForm(instance=assessment)
        status = 200

    form_html = render_to_string(
        'patients/partials/assessment_update_form.html',
        {'form': form, 'patient': patient, 'assessment': assessment},
        request=request
    )

    return JsonResponse({
        'success': request.method == 'GET',
        'form_html': form_html,
        'message': 'Please correct the highlighted errors and try again.' if request.method == 'POST' else '',
    }, status=status)

@login_required
def patient_register(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            patient = form.save(commit=False)
            patient.registered_by = request.user
            # Generate patient ID
            last_patient = Patient.objects.order_by('-id').first()
            if last_patient and '-' in last_patient.patient_id:
                try:
                    last_id = int(last_patient.patient_id.split('-')[1])
                    patient.patient_id = f"PT-{last_id + 1:06d}"
                except (ValueError, IndexError):
                    # If parsing fails, get the count and add 1
                    patient_count = Patient.objects.count()
                    patient.patient_id = f"PT-{patient_count + 1:06d}"
            else:
                patient.patient_id = "PT-000001"
            patient.save()
            messages.success(request, f'Patient {patient.get_full_name()} registered successfully!')
            return redirect('patients:patient_detail', patient_id=patient.patient_id)
    else:
        form = PatientForm()
    
    return render(request, 'patients/patient_register.html', {'form': form})

@login_required
def visiting_patient_register(request):
    if request.method == 'POST':
        form = VisitingPatientForm(request.POST)
        if form.is_valid():
            patient = form.save(commit=False)
            patient.registered_by = request.user
            patient.is_visiting_patient = True
            
            # Generate visiting patient ID with VP prefix
            last_visiting_patient = Patient.objects.filter(is_visiting_patient=True).order_by('-id').first()
            if last_visiting_patient and 'VP-' in last_visiting_patient.patient_id:
                try:
                    last_id = int(last_visiting_patient.patient_id.split('-')[1])
                    patient.patient_id = f"VP-{last_id + 1:06d}"
                except (ValueError, IndexError):
                    # If parsing fails, get the count and add 1
                    visiting_count = Patient.objects.filter(is_visiting_patient=True).count()
                    patient.patient_id = f"VP-{visiting_count + 1:06d}"
            else:
                patient.patient_id = "VP-000001"
            
            patient.save()
            messages.success(request, f'Visiting patient {patient.patient_id} registered successfully!')
            return redirect('patients:patient_detail', patient_id=patient.patient_id)
    else:
        form = VisitingPatientForm()
    
    return render(request, 'patients/visiting_patient_register.html', {'form': form})

@medical_staff_required
def record_vitals(request, patient_id):
    patient = get_object_or_404(Patient, patient_id=patient_id)
    
    if request.method == 'POST':
        form = VitalSignsForm(request.POST)
        if form.is_valid():
            vital_signs = form.save(commit=False)
            vital_signs.patient = patient
            vital_signs.recorded_by = request.user
            vital_signs.save()
            messages.success(request, 'Vital signs recorded successfully!')
            return redirect('patients:patient_detail', patient_id=patient.patient_id)
    else:
        form = VitalSignsForm()
    
    context = {
        'form': form,
        'patient': patient,
    }
    return render(request, 'patients/record_vitals.html', context)

@medical_staff_required
def triage_patient(request, patient_id):
    patient = get_object_or_404(Patient, patient_id=patient_id)
    
    if request.method == 'POST':
        form = TriageForm(request.POST)
        if form.is_valid():
            triage = form.save(commit=False)
            triage.patient = patient
            triage.triaged_by = request.user
            triage.save()
            messages.success(request, 'Patient triage completed successfully!')
            return redirect('patients:patient_detail', patient_id=patient.patient_id)
    else:
        form = TriageForm()
    
    # Get previous triage records for the template
    previous_triages = patient.triages.all()[:5]
    
    context = {
        'form': form,
        'patient': patient,
        'previous_triages': previous_triages,
    }
    return render(request, 'patients/triage.html', context)

@medical_staff_required
def assessment_create(request, patient_id):
    patient = get_object_or_404(Patient, patient_id=patient_id)
    
    # Determine department from URL parameter or user role
    department = request.GET.get('department')
    if not department:
        # Default based on user role
        if request.user.role == 'doctor':
            department = 'physiotherapy'
        elif request.user.role == 'nutritionist':
            department = 'nutrition'
        else:
            department = 'general'
    
    # Role-based access control - prevent cross-department access
    if request.user.role == 'physiotherapist' and department != 'physiotherapy':
        messages.error(request, 'Physiotherapists can only create physiotherapy assessments.')
        return redirect('patients:patient_detail', patient_id=patient.patient_id)
    
    if request.user.role == 'nutritionist' and department != 'nutrition':
        messages.error(request, 'Nutritionists can only create nutrition assessments.')
        return redirect('patients:patient_detail', patient_id=patient.patient_id)
    
    # Select appropriate form based on department
    if department == 'physiotherapy':
        FormClass = PhysiotherapyAssessmentForm
        template_name = 'patients/physiotherapy_assessment.html'
    elif department == 'nutrition':
        FormClass = NutritionAssessmentForm
        template_name = 'patients/nutrition_assessment.html'
    else:
        FormClass = AssessmentForm
        template_name = 'patients/assessment.html'
    
    if request.method == 'POST':
        form = FormClass(request.POST)
        if form.is_valid():
            assessment = form.save(commit=False)
            assessment.patient = patient
            assessment.assessed_by = request.user
            assessment.department = department
            assessment.save()

            if department == 'physiotherapy':
                crf_data = {}
                for key, value in request.POST.items():
                    if not key.startswith('crf_'):
                        continue
                    cleaned = value.strip() if isinstance(value, str) else value
                    if cleaned in (None, ''):
                        continue
                    try:
                        crf_data[key] = int(cleaned)
                    except (TypeError, ValueError):
                        crf_data[key] = cleaned

                if crf_data:
                    PhysiotherapyClinicalReasoningForm.objects.update_or_create(
                        assessment=assessment,
                        defaults={'crf_data': crf_data},
                    )

            messages.success(request, f'{department.title()} assessment completed successfully!')
            return redirect('patients:patient_detail', patient_id=patient.patient_id)
        else:
            # Add error message for debugging
            messages.error(request, 'Please correct the errors below and try again.')
    else:
        form = FormClass()
        # Pre-populate department
        form.initial['department'] = department
        
        # Pre-populate related_triage if this is a first visit and there's a recent triage
        recent_triage = patient.triages.order_by('-triage_date').first()
        if recent_triage:
            form.initial['related_triage'] = recent_triage.id
            form.initial['chief_complaint'] = recent_triage.chief_complaint
            form.initial['assessment_type'] = 'first_visit'  # Set default assessment type
        else:
            form.initial['assessment_type'] = 'follow_up'  # Default for no triage
    
    # Get available triages for linking
    available_triages = patient.triages.order_by('-triage_date')[:10]
    
    # Get previous assessments for the template
    previous_assessments = patient.assessments.all()[:5]
    
    context = {
        'form': form,
        'patient': patient,
        'available_triages': available_triages,
        'previous_assessments': previous_assessments,
        'department': department,
    }
    return render(request, template_name, context)

@medical_staff_required
def physiotherapy_assessment(request, patient_id):
    """Dedicated physiotherapy assessment view"""
    # Simulate department parameter by modifying request
    request.GET = request.GET.copy()
    request.GET['department'] = 'physiotherapy'
    return assessment_create(request, patient_id)

@medical_staff_required
def nutrition_assessment(request, patient_id):
    """Dedicated nutrition assessment view"""
    # Simulate department parameter by modifying request
    request.GET = request.GET.copy()
    request.GET['department'] = 'nutrition'
    return assessment_create(request, patient_id)

# Legacy view - keep for backward compatibility
@medical_staff_required
def triage_assessment(request, patient_id):
    patient = get_object_or_404(Patient, patient_id=patient_id)
    
    if request.method == 'POST':
        form = TriageAssessmentForm(request.POST)
        if form.is_valid():
            assessment = form.save(commit=False)
            assessment.patient = patient
            assessment.assessed_by = request.user
            assessment.save()
            messages.success(request, 'Triage assessment completed successfully!')
            return redirect('patients:patient_detail', patient_id=patient.patient_id)
    else:
        form = TriageAssessmentForm()
    
    # Get previous assessments for the template
    previous_assessments = patient.triage_assessments.all()[:5]
    
    context = {
        'form': form,
        'patient': patient,
        'previous_assessments': previous_assessments,
    }
    return render(request, 'patients/triage_assessment.html', context)

@login_required
def patient_details_print(request, patient_id):
    patient = get_object_or_404(Patient, patient_id=patient_id)
    
    # Get clinic settings for header
    clinic_settings = ClinicSettings.get_settings()
    
    # Get recent vital signs and triage assessments
    vital_signs = patient.vital_signs.order_by('-recorded_date')[:5]
    triage_assessments = patient.triage_assessments.order_by('-assessment_date')[:3]
    
    context = {
        'patient': patient,
        'vital_signs': vital_signs,
        'triage_assessments': triage_assessments,
        'clinic_settings': clinic_settings,
    }
    return render(request, 'patients/patient_details_print.html', context)

@login_required
def vital_signs_print(request, patient_id, vital_id):
    """Print view for a single vital signs record"""
    from django.utils import timezone
    
    patient = get_object_or_404(Patient, patient_id=patient_id)
    vital = get_object_or_404(VitalSigns, pk=vital_id, patient=patient)
    clinic_settings = ClinicSettings.get_settings()
    
    context = {
        'patient': patient,
        'vital': vital,
        'clinic_settings': clinic_settings,
        'now': timezone.now(),
    }
    
    return render(request, 'patients/vital_signs_print.html', context)

@login_required
def medical_info_print(request, patient_id):
    """Print view for comprehensive medical information"""
    from django.utils import timezone
    
    patient = get_object_or_404(Patient, patient_id=patient_id)
    clinic_settings = ClinicSettings.get_settings()
    
    # Get vital signs
    vital_signs = patient.vital_signs.order_by('-recorded_date')[:10]
    
    # Get assessments - filtered by user role
    assessments_query = patient.assessments.select_related('assessed_by')
    
    if request.user.role == 'physiotherapist':
        # Physiotherapists can only see physiotherapy assessments
        assessments = assessments_query.filter(department='physiotherapy').order_by('-assessment_date')[:10]
    elif request.user.role == 'nutritionist':
        # Nutritionists can only see nutrition assessments
        assessments = assessments_query.filter(department='nutrition').order_by('-assessment_date')[:10]
    else:
        # Doctors, admins, nurses can see all assessments
        assessments = assessments_query.order_by('-assessment_date')[:10]
    
    # Get lab results if available
    try:
        from laboratory.models import LabResult
        lab_results = LabResult.objects.filter(request__patient=patient).order_by('-date_reported')[:10]
    except:
        lab_results = None
    
    # Get prescriptions
    try:
        from pharmacy.models import Prescription
        prescriptions = Prescription.objects.filter(patient=patient).prefetch_related('items__medication').order_by('-prescribed_date')[:10]
    except:
        prescriptions = None
    
    context = {
        'patient': patient,
        'vital_signs': vital_signs,
        'assessments': assessments,
        'lab_results': lab_results,
        'prescriptions': prescriptions,
        'clinic_settings': clinic_settings,
        'now': timezone.now(),
    }
    
    return render(request, 'patients/medical_info_print.html', context)


class PatientUpdateView(UpdateView):
    model = Patient
    form_class = PatientForm
    template_name = 'patients/patient_form.html'
    context_object_name = 'patient'
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Handle AJAX request
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'Patient {self.object.get_full_name()} updated successfully!',
                'redirect_url': self.get_success_url()
            })
        
        return response
    
    def form_invalid(self, form):
        # Handle AJAX request for errors
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })
        
        return super().form_invalid(form)
    
    def get_success_url(self):
        return reverse_lazy('patients:patient_detail', kwargs={'patient_id': self.object.patient_id})
    
    def get_queryset(self):
        return Patient.objects.all()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Update {self.object.get_full_name()}\'s Profile'
        return context


@login_required
def patient_medical_records(request, patient_id):
    """View for displaying a patient's medical records."""
    patient = get_object_or_404(Patient, patient_id=patient_id)
    vital_signs = patient.vital_signs.order_by('-recorded_date').all()
    triages = patient.triages.order_by('-triage_date').all()
    assessments = patient.assessments.order_by('-assessment_date').all()
    # Keep legacy for backward compatibility
    triage_assessments = patient.triage_assessments.order_by('-assessment_date').all()
    
    context = {
        'patient': patient,
        'vital_signs': vital_signs,
        'triages': triages,
        'assessments': assessments,
        'triage_assessments': triage_assessments,  # Keep for backward compatibility
    }
    return render(request, 'patients/medical_records.html', context)


# AJAX-only assessment views
@login_required
@medical_staff_required
def physiotherapy_assessment_ajax(request, patient_id):
    """AJAX-only physiotherapy assessment view"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Check if request is AJAX
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'error': 'AJAX request required'}, status=400)
    
    # Role-based access control - only physiotherapists, doctors, admins, and nurses can create physiotherapy assessments
    if request.user.role == 'nutritionist':
        return JsonResponse({'error': 'Nutritionists cannot create physiotherapy assessments'}, status=403)
    
    patient = get_object_or_404(Patient, patient_id=patient_id, is_active=True)
    form = PhysiotherapyAssessmentForm(request.POST)
    
    if form.is_valid():
        assessment = form.save(commit=False)
        assessment.patient = patient
        assessment.assessed_by = request.user
        assessment.department = 'physiotherapy'
        
        # Link to appointment if provided
        appointment_id = request.POST.get('appointment_id')
        if appointment_id:
            try:
                appointment = Appointment.objects.get(id=appointment_id, patient=patient)
                assessment.related_appointment = appointment
            except Appointment.DoesNotExist:
                pass
        
        assessment.save()

        crf_data = {}
        for key, value in request.POST.items():
            if not key.startswith('crf_'):
                continue
            cleaned = value.strip() if isinstance(value, str) else value
            if cleaned in (None, ''):
                continue
            try:
                crf_data[key] = int(cleaned)
            except (TypeError, ValueError):
                crf_data[key] = cleaned

        if crf_data:
            PhysiotherapyClinicalReasoningForm.objects.update_or_create(
                assessment=assessment,
                defaults={'crf_data': crf_data},
            )
        
        # Handle follow-up appointment creation
        appointment_created = False
        follow_up_appointment_id = None
        if assessment.follow_up_required and assessment.follow_up_date:
            try:
                # Get or create a physiotherapy service
                service, service_created = Service.objects.get_or_create(
                    name='Physiotherapy Follow-up',
                    category='physiotherapy',
                    defaults={
                        'description': 'Follow-up physiotherapy session',
                        'duration_minutes': 60,
                        'base_price': 0.00
                    }
                )
                
                print(f"Service {'created' if service_created else 'found'}: {service.name}")
                
                # Create the appointment
                appointment = Appointment.objects.create(
                    patient=patient,
                    service=service,
                    provider=request.user,
                    appointment_date=assessment.follow_up_date,
                    appointment_time=datetime.now().time(),  # Use current time
                    duration_minutes=service.duration_minutes,
                    status='scheduled',
                    notes=f"Follow-up from assessment: {assessment.follow_up_instructions}" if assessment.follow_up_instructions else "Follow-up appointment from physiotherapy assessment"
                )
                appointment_created = True
                follow_up_appointment_id = appointment.id
                print(f"✅ Physiotherapy follow-up appointment created: ID {appointment.id}, Date: {appointment.appointment_date}")
            except Exception as e:
                # Log the error but don't fail the assessment
                print(f"Error creating follow-up appointment: {e}")
                import traceback
                traceback.print_exc()
        
        success_message = 'Physiotherapy assessment completed successfully!'
        if appointment_created:
            success_message += f' Follow-up appointment scheduled for {assessment.follow_up_date.strftime("%B %d, %Y")}.'
        
        return JsonResponse({
            'success': True,
            'message': success_message,
            'assessment_id': assessment.id,
            'appointment_created': appointment_created,
            'follow_up_date': assessment.follow_up_date.strftime("%Y-%m-%d") if assessment.follow_up_date else None
        })
    else:
        # Return form errors for client-side display
        errors = {}
        for field, error_list in form.errors.items():
            errors[field] = error_list
        
        return JsonResponse({
            'success': False,
            'errors': errors,
            'message': 'Please correct the errors below and try again.'
        }, status=400)


@login_required
@medical_staff_required
def nutrition_assessment_ajax(request, patient_id):
    """AJAX-only nutrition assessment view"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Check if request is AJAX
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'error': 'AJAX request required'}, status=400)
    
    # Role-based access control - only nutritionists, doctors, admins, and nurses can create nutrition assessments
    if request.user.role == 'physiotherapist':
        return JsonResponse({'error': 'Physiotherapists cannot create nutrition assessments'}, status=403)
    
    patient = get_object_or_404(Patient, patient_id=patient_id, is_active=True)
    form = NutritionAssessmentForm(request.POST)
    
    if form.is_valid():
        assessment = form.save(commit=False)
        assessment.patient = patient
        assessment.assessed_by = request.user
        assessment.department = 'nutrition'
        
        # Link to appointment if provided
        appointment_id = request.POST.get('appointment_id')
        if appointment_id:
            try:
                appointment = Appointment.objects.get(id=appointment_id, patient=patient)
                assessment.related_appointment = appointment
            except Appointment.DoesNotExist:
                pass
        
        assessment.save()
        
        # Handle follow-up appointment creation
        appointment_created = False
        follow_up_appointment_id = None
        if assessment.follow_up_required and assessment.follow_up_date:
            try:
                # Get or create a nutrition service
                service, service_created = Service.objects.get_or_create(
                    name='Nutrition Follow-up',
                    category='nutrition',
                    defaults={
                        'description': 'Follow-up nutrition consultation',
                        'duration_minutes': 45,
                        'base_price': 0.00
                    }
                )
                
                print(f"Service {'created' if service_created else 'found'}: {service.name}")
                
                # Create the appointment
                appointment = Appointment.objects.create(
                    patient=patient,
                    service=service,
                    provider=request.user,
                    appointment_date=assessment.follow_up_date,
                    appointment_time=datetime.now().time(),  # Use current time
                    duration_minutes=service.duration_minutes,
                    status='scheduled',
                    notes=f"Follow-up from assessment: {assessment.follow_up_instructions}" if assessment.follow_up_instructions else "Follow-up appointment from nutrition assessment"
                )
                appointment_created = True
                follow_up_appointment_id = appointment.id
                print(f"✅ Nutrition follow-up appointment created: ID {appointment.id}, Date: {appointment.appointment_date}")
            except Exception as e:
                # Log the error but don't fail the assessment
                print(f"Error creating follow-up appointment: {e}")
                import traceback
                traceback.print_exc()
        
        success_message = 'Nutrition assessment completed successfully!'
        if appointment_created:
            success_message += f' Follow-up appointment scheduled for {assessment.follow_up_date.strftime("%B %d, %Y")}.'
        
        return JsonResponse({
            'success': True,
            'message': success_message,
            'assessment_id': assessment.id,
            'appointment_created': appointment_created,
            'follow_up_date': assessment.follow_up_date.strftime("%Y-%m-%d") if assessment.follow_up_date else None
        })
    else:
        # Return form errors for client-side display
        errors = {}
        for field, error_list in form.errors.items():
            errors[field] = error_list
        
        # Log the errors for debugging
        print(f"Nutrition Assessment Form Errors: {form.errors}")
        print(f"POST Data Keys: {list(request.POST.keys())}")
        
        return JsonResponse({
            'success': False,
            'errors': errors,
            'message': 'Please correct the errors below and try again.'
        }, status=400)


@medical_staff_required
def general_assessment_ajax(request, patient_id):
    """AJAX-only general assessment view"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Check if request is AJAX
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'error': 'AJAX request required'}, status=400)
    
    patient = get_object_or_404(Patient, patient_id=patient_id, is_active=True)
    form = AssessmentForm(request.POST)
    
    if form.is_valid():
        assessment = form.save(commit=False)
        assessment.patient = patient
        assessment.assessed_by = request.user
        # Set department from form or default to general
        if not assessment.department:
            assessment.department = 'general'
        
        # Link to appointment if provided
        appointment_id = request.POST.get('appointment_id')
        if appointment_id:
            try:
                from appointments.models import Appointment
                appointment = Appointment.objects.get(id=appointment_id, patient=patient)
                assessment.related_appointment = appointment
            except Appointment.DoesNotExist:
                pass
        
        assessment.save()
        
        # Handle follow-up appointment creation
        appointment_created = False
        follow_up_required = request.POST.get('follow_up_required') == 'on'
        follow_up_date = request.POST.get('follow_up_date')
        follow_up_instructions = request.POST.get('follow_up_instructions', '')
        
        if follow_up_required and follow_up_date:
            try:
                # Get or create a general consultation service
                service, created = Service.objects.get_or_create(
                    name='General Follow-up Consultation',
                    category='consultation',
                    defaults={
                        'description': 'Follow-up general medical consultation',
                        'duration_minutes': 30,
                        'base_price': 0.00
                    }
                )
                
                # Create the appointment
                appointment = Appointment.objects.create(
                    patient=patient,
                    service=service,
                    provider=request.user,
                    appointment_date=follow_up_date,
                    appointment_time=datetime.now().time(),  # Use current time
                    duration_minutes=service.duration_minutes,
                    status='scheduled',
                    notes=f"Follow-up from assessment: {follow_up_instructions}" if follow_up_instructions else "Follow-up appointment from general assessment"
                )
                appointment_created = True
            except Exception as e:
                # Log the error but don't fail the assessment
                print(f"Error creating follow-up appointment: {e}")
        
        return JsonResponse({
            'success': True,
            'message': 'General assessment completed successfully!',
            'assessment_id': assessment.id,
            'appointment_created': appointment_created
        })
    else:
        # Return form errors for client-side display
        errors = {}
        for field, error_list in form.errors.items():
            errors[field] = error_list
        
        return JsonResponse({
            'success': False,
            'errors': errors,
            'message': 'Please correct the errors below and try again.'
        }, status=400)

@login_required
@medical_staff_required
def physiotherapist_patients(request):
    """
    Comprehensive view for physiotherapists to see ALL patients in the physiotherapy department:
    - Patients currently in the physiotherapy department (via triage)
    - Patients with physiotherapy assessments (by any physiotherapist)
    - Patients with physiotherapy appointments
    - Patients previously worked on in the department
    """
    # Check if user is a doctor/physiotherapist
    if request.user.role != 'doctor':
        messages.error(request, 'Access denied. This page is only for physiotherapists.')
        return redirect('patients:dashboard')
    
    # Get filter parameters
    status_filter = request.GET.get('status', 'all')
    search_query = request.GET.get('search', '')
    sort_by = request.GET.get('sort', '-last_assessment')
    view_type = request.GET.get('view', 'all')  # 'all' or 'my_patients'
    
    # Get ALL patients in the entire system (not just physiotherapy)
    all_patients = Patient.objects.filter(is_active=True).distinct()
    
    # Get MY patients (only those I've worked with or have appointments with)
    my_patients = Patient.objects.filter(
        Q(assessments__assessed_by=request.user) |
        Q(appointments__provider=request.user),
        is_active=True
    ).distinct()
    
    # Choose which patient set to display based on view_type
    if view_type == 'my_patients':
        patients = my_patients
    else:
        patients = all_patients
    
    # Debug: Show initial patient count
    initial_count = patients.count()
    if initial_count == 0:
        messages.warning(request, 'No patients found in physiotherapy department. Please ensure patients have been triaged to physiotherapy or have physiotherapy assessments/appointments.')
    
    # Apply search filter
    if search_query:
        patients = patients.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(patient_id__icontains=search_query) |
            Q(phone__icontains=search_query)
        )
    
    # Annotate patients with additional data (all assessments and appointments)
    from django.db.models import Count, Max, Prefetch, Q as QFilter
    
    patients = patients.annotate(
        assessment_count=Count('assessments', distinct=True),
        last_assessment_date=Max('assessments__assessment_date'),
        appointment_count=Count('appointments', distinct=True)
    )
    
    # Apply status filter
    if status_filter == 'active':
        # Patients with upcoming appointments or recent assessments (within 30 days)
        from datetime import timedelta
        from django.utils import timezone
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        patients = patients.filter(
            Q(appointments__status__in=['scheduled', 'confirmed', 'in_progress'],
              appointments__appointment_date__gte=timezone.now().date()) |
            Q(assessments__assessment_date__gte=thirty_days_ago)
        ).distinct()
    elif status_filter == 'follow_up':
        # Patients requiring follow-up
        patients = patients.filter(
            assessments__follow_up_required=True,
            assessments__follow_up_date__gte=datetime.now().date()
        ).distinct()
    elif status_filter == 'completed':
        # Patients with completed appointments
        patients = patients.filter(
            appointments__status='completed'
        ).distinct()
    # If status_filter is 'all', don't apply any additional filtering - show all patients
    
    # Debug: Show filtered patient count
    filtered_count = patients.count()
    if status_filter != 'all' and filtered_count < initial_count:
        messages.info(request, f'Showing {filtered_count} patients with "{status_filter}" status. Change filter to "All Patients" to see all {initial_count} patients.')
    
    # Apply sorting (with fallback to ensure consistent ordering)
    if sort_by == '-last_assessment':
        patients = patients.order_by('-last_assessment_date', 'id')
    elif sort_by == 'name':
        patients = patients.order_by('first_name', 'last_name', 'id')
    elif sort_by == '-assessment_count':
        patients = patients.order_by('-assessment_count', 'id')
    else:
        patients = patients.order_by('id')  # Default ordering
    
    # Prefetch related data for efficiency (all patient data)
    patients = patients.prefetch_related(
        Prefetch('assessments', queryset=Assessment.objects.all().order_by('-assessment_date')),
        Prefetch('appointments', queryset=Appointment.objects.all().order_by('-appointment_date')),
        'vital_signs',
        'triages'
    )
    
    # Debug: Log the actual query and count before pagination
    final_count = patients.count()
    print(f"DEBUG: Final patient count before pagination: {final_count}")
    print(f"DEBUG: Status filter: {status_filter}")
    print(f"DEBUG: Sort by: {sort_by}")
    print(f"DEBUG: Search query: {search_query}")
    
    # Show debug info to user
    if view_type == 'my_patients':
        messages.info(request, f'Showing {final_count} of your patients.')
    else:
        messages.info(request, f'Showing {final_count} total patients in the system.')
    
    # Pagination
    paginator = Paginator(patients, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Calculate statistics (physiotherapy department only)
    total_patients = patients.count()
    total_assessments = Assessment.objects.filter(department='physiotherapy').count()
    total_appointments = Appointment.objects.filter(service__category='physiotherapy').count()
    
    # Upcoming appointments (physiotherapy appointments only)
    upcoming_appointments = Appointment.objects.filter(
        service__category='physiotherapy',
        status__in=['scheduled', 'confirmed'],
        appointment_date__gte=datetime.now().date()
    ).select_related('patient', 'provider', 'service').order_by('appointment_date', 'appointment_time')[:10]
    
    # Patients requiring follow-up (physiotherapy patients)
    follow_up_patients = Patient.objects.filter(
        assessments__department='physiotherapy',
        assessments__follow_up_required=True,
        assessments__follow_up_date__gte=datetime.now().date()
    ).distinct().count()
    
    context = {
        'page_obj': page_obj,
        'patients': page_obj,
        'total_patients': total_patients,
        'total_assessments': total_assessments,
        'total_appointments': total_appointments,
        'follow_up_patients': follow_up_patients,
        'upcoming_appointments': upcoming_appointments,
        'status_filter': status_filter,
        'search_query': search_query,
        'sort_by': sort_by,
        'view_type': view_type,
        'all_patients_count': all_patients.count(),
        'my_patients_count': my_patients.count(),
    }
    
    return render(request, 'patients/physiotherapist_patients.html', context)

@login_required
@medical_staff_required
def nutritionist_patients(request):
    """
    Comprehensive view for nutritionists to see ALL patients in the clinic:
    - All patients in the system
    - Patients with nutrition assessments
    - Patients with nutrition appointments
    - Patients previously worked on by the nutritionist
    """
    # Check if user is a nutritionist
    if request.user.role != 'nutritionist':
        messages.error(request, 'Access denied. This page is only for nutritionists.')
        return redirect('patients:dashboard')
    
    # Get filter parameters
    status_filter = request.GET.get('status', 'all')
    search_query = request.GET.get('search', '')
    sort_by = request.GET.get('sort', '-last_assessment')
    view_type = request.GET.get('view', 'all')  # 'all' or 'my_patients'
    
    # Get ALL patients in the entire system
    all_patients = Patient.objects.filter(is_active=True).distinct()
    
    # Get MY patients (only those I've worked with or have appointments with)
    my_patients = Patient.objects.filter(
        Q(assessments__assessed_by=request.user) |
        Q(appointments__provider=request.user),
        is_active=True
    ).distinct()
    
    # Choose which patient set to display based on view_type
    if view_type == 'my_patients':
        patients = my_patients
    else:
        patients = all_patients
    
    # Debug: Show initial patient count
    initial_count = patients.count()
    if initial_count == 0:
        messages.warning(request, 'No patients found. Please ensure patients are registered in the system.')
    
    # Apply search filter
    if search_query:
        patients = patients.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(patient_id__icontains=search_query) |
            Q(phone__icontains=search_query)
        )
    
    # Annotate patients with additional data (all assessments and appointments)
    from django.db.models import Count, Max, Prefetch, Q as QFilter
    
    patients = patients.annotate(
        assessment_count=Count('assessments', distinct=True),
        last_assessment_date=Max('assessments__assessment_date'),
        appointment_count=Count('appointments', distinct=True)
    )
    
    # Apply status filter
    if status_filter == 'active':
        # Patients with upcoming appointments or recent assessments (within 30 days)
        from datetime import timedelta
        from django.utils import timezone
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        patients = patients.filter(
            Q(appointments__status__in=['scheduled', 'confirmed', 'in_progress'],
              appointments__appointment_date__gte=timezone.now().date()) |
            Q(assessments__assessment_date__gte=thirty_days_ago)
        ).distinct()
    elif status_filter == 'follow_up':
        # Patients requiring follow-up
        patients = patients.filter(
            assessments__follow_up_required=True,
            assessments__follow_up_date__gte=datetime.now().date()
        ).distinct()
    elif status_filter == 'completed':
        # Patients with completed appointments
        patients = patients.filter(
            appointments__status='completed'
        ).distinct()
    
    # Debug: Show filtered patient count
    filtered_count = patients.count()
    if status_filter != 'all' and filtered_count < initial_count:
        messages.info(request, f'Showing {filtered_count} patients with "{status_filter}" status. Change filter to "All Patients" to see all {initial_count} patients.')
    
    # Apply sorting (with fallback to ensure consistent ordering)
    if sort_by == '-last_assessment':
        patients = patients.order_by('-last_assessment_date', 'id')
    elif sort_by == 'name':
        patients = patients.order_by('first_name', 'last_name', 'id')
    elif sort_by == '-assessment_count':
        patients = patients.order_by('-assessment_count', 'id')
    else:
        patients = patients.order_by('id')  # Default ordering
    
    # Prefetch related data for efficiency (all patient data)
    patients = patients.prefetch_related(
        Prefetch('assessments', queryset=Assessment.objects.all().order_by('-assessment_date')),
        Prefetch('appointments', queryset=Appointment.objects.all().order_by('-appointment_date')),
        'vital_signs',
        'triages'
    )
    
    # Debug: Log the actual query and count before pagination
    final_count = patients.count()
    
    # Show debug info to user
    if view_type == 'my_patients':
        messages.info(request, f'Showing {final_count} of your patients.')
    else:
        messages.info(request, f'Showing {final_count} total patients in the system.')
    
    # Pagination
    paginator = Paginator(patients, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Calculate statistics (nutrition department only)
    total_patients = patients.count()
    total_assessments = Assessment.objects.filter(department='nutrition').count()
    total_appointments = Appointment.objects.filter(service__category='nutrition').count()
    
    # Upcoming appointments (nutrition appointments only)
    upcoming_appointments = Appointment.objects.filter(
        service__category='nutrition',
        status__in=['scheduled', 'confirmed'],
        appointment_date__gte=datetime.now().date()
    ).select_related('patient', 'provider', 'service').order_by('appointment_date', 'appointment_time')[:10]
    
    # Patients requiring follow-up (nutrition patients)
    follow_up_patients = Patient.objects.filter(
        assessments__department='nutrition',
        assessments__follow_up_required=True,
        assessments__follow_up_date__gte=datetime.now().date()
    ).distinct().count()
    
    context = {
        'page_obj': page_obj,
        'patients': page_obj,
        'total_patients': total_patients,
        'total_assessments': total_assessments,
        'total_appointments': total_appointments,
        'follow_up_patients': follow_up_patients,
        'upcoming_appointments': upcoming_appointments,
        'status_filter': status_filter,
        'search_query': search_query,
        'sort_by': sort_by,
        'view_type': view_type,
        'all_patients_count': all_patients.count(),
        'my_patients_count': my_patients.count(),
    }
    
    return render(request, 'patients/nutritionist_patients.html', context)


# ==================== AJAX-ONLY VIEWS ====================

@login_required
@medical_staff_required
def vital_signs_record_ajax(request, patient_id):
    """
    Vital signs recording view - handles both regular POST and AJAX
    """
    import logging
    from django.contrib import messages
    from django.shortcuts import redirect
    from django.urls import reverse
    
    logger = logging.getLogger(__name__)
    
    # Only accept POST requests
    if request.method != 'POST':
        messages.error(request, 'Invalid request method')
        return redirect('patients:patient_detail', patient_id=patient_id)
    
    # Check if AJAX request
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    logger.info("=" * 60)
    logger.info(f"🔍 VITAL SIGNS REQUEST INITIATED")
    logger.info(f"🔍 Patient ID: {patient_id}")
    logger.info(f"🔍 User: {request.user.username}")
    logger.info(f"🔍 Is AJAX: {is_ajax}")
    logger.info("=" * 60)
    
    # Get patient
    try:
        patient = Patient.objects.get(patient_id=patient_id)
        logger.info(f"✅ Patient found: {patient.get_full_name()}")
    except Patient.DoesNotExist:
        logger.error(f"❌ Patient not found: {patient_id}")
        if is_ajax:
            return JsonResponse({
                'success': False,
                'error': 'Patient not found'
            }, status=404)
        else:
            messages.error(request, f'Patient {patient_id} not found')
            return redirect('patients:patient_list')
    
    # Log POST data
    logger.info(f"📋 POST Data:")
    for key, value in request.POST.items():
        if key != 'csrfmiddlewaretoken':
            logger.info(f"   - {key}: {value}")
    
    # Validate form
    form = VitalSignsForm(request.POST)
    
    if form.is_valid():
        try:
            # Save vital signs
            vital_signs = form.save(commit=False)
            vital_signs.patient = patient
            vital_signs.recorded_by = request.user
            vital_signs.save()
            
            logger.info("=" * 60)
            logger.info(f"✅ VITAL SIGNS SAVED SUCCESSFULLY")
            logger.info(f"✅ Vital ID: {vital_signs.id}")
            logger.info(f"✅ Height: {vital_signs.height} cm")
            logger.info(f"✅ Weight: {vital_signs.weight} kg")
            logger.info(f"✅ BMI: {vital_signs.bmi}")
            logger.info(f"✅ Blood Pressure: {vital_signs.blood_pressure_systolic}/{vital_signs.blood_pressure_diastolic}")
            logger.info(f"✅ Recorded by: {request.user.username}")
            logger.info("=" * 60)
            
            success_message = f'✅ Vital signs for {patient.get_full_name()} recorded successfully!'
            
            if is_ajax:
                # AJAX response
                return JsonResponse({
                    'success': True,
                    'message': success_message,
                    'data': {
                        'vital_id': vital_signs.id,
                        'height': str(vital_signs.height),
                        'weight': str(vital_signs.weight),
                        'bmi': str(vital_signs.bmi) if vital_signs.bmi else None,
                    },
                    'redirect_url': reverse('patients:patient_detail', kwargs={'patient_id': patient.patient_id})
                })
            else:
                # Regular POST - redirect with success message
                messages.success(request, success_message)
                return redirect('patients:patient_detail', patient_id=patient.patient_id)
            
        except Exception as e:
            logger.error("=" * 60)
            logger.error(f"❌ ERROR SAVING VITAL SIGNS")
            logger.error(f"❌ Exception: {str(e)}")
            logger.error("=" * 60)
            
            error_message = f'Error saving vital signs: {str(e)}'
            
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'error': error_message
                }, status=500)
            else:
                messages.error(request, error_message)
                return redirect('patients:patient_detail', patient_id=patient.patient_id)
    
    else:
        # Form validation failed
        logger.error("=" * 60)
        logger.error(f"❌ FORM VALIDATION FAILED")
        
        error_messages = []
        for field, error_list in form.errors.items():
            for error in error_list:
                error_messages.append(f"{field}: {error}")
                logger.error(f"   - {field}: {error}")
        
        logger.error("=" * 60)
        
        if is_ajax:
            errors = {}
            for field, error_list in form.errors.items():
                errors[field] = [str(error) for error in error_list]
            
            return JsonResponse({
                'success': False,
                'errors': errors,
                'message': 'Please correct the errors: ' + ', '.join(error_messages)
            }, status=400)
        else:
            # Regular POST - show errors and redirect
            for error_msg in error_messages:
                messages.error(request, error_msg)
            return redirect('patients:patient_detail', patient_id=patient.patient_id)


@login_required
@medical_staff_required
def triage_create_ajax(request, patient_id):
    """AJAX-only triage creation view"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Check if request is AJAX
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'error': 'AJAX request required'}, status=400)
    
    patient = get_object_or_404(Patient, patient_id=patient_id)
    
    form = TriageForm(request.POST)
    if form.is_valid():
        triage = form.save(commit=False)
        triage.patient = patient
        triage.triaged_by = request.user
        triage.save()
        
        from django.urls import reverse
        return JsonResponse({
            'success': True,
            'message': f'Triage for {patient.get_full_name()} completed successfully!',
            'triage_id': triage.id,
            'redirect_url': reverse('patients:patient_detail', kwargs={'patient_id': patient.patient_id})
        })
    else:
        # Return form errors for client-side display
        errors = {}
        for field, error_list in form.errors.items():
            errors[field] = error_list
        
        return JsonResponse({
            'success': False,
            'errors': errors,
            'message': 'Please correct the errors below and try again.'
        }, status=400)


@login_required
def assessment_print(request, patient_id, assessment_id):
    """Display assessment in printable format"""
    patient = get_object_or_404(Patient, patient_id=patient_id)
    assessment = get_object_or_404(Assessment, id=assessment_id, patient=patient)
    
    # Get clinic settings
    try:
        clinic_settings = ClinicSettings.objects.first()
    except:
        clinic_settings = None
    
    context = {
        'patient': patient,
        'assessment': assessment,
        'clinic_settings': clinic_settings,
    }
    
    return render(request, 'patients/assessment_print.html', context)


@login_required
def assessment_print_pdf(request, patient_id, assessment_id):
    """Generate and download assessment as PDF using same template as print view"""
    patient = get_object_or_404(Patient, patient_id=patient_id)
    assessment = get_object_or_404(Assessment, id=assessment_id, patient=patient)
    
    # Get clinic settings
    try:
        clinic_settings = ClinicSettings.objects.first()
    except:
        clinic_settings = None
    
    # Build absolute logo path for PDF
    logo_path = None
    if clinic_settings and clinic_settings.logo:
        logo_path = os.path.join(settings.MEDIA_ROOT, str(clinic_settings.logo))
    
    context = {
        'patient': patient,
        'assessment': assessment,
        'clinic_settings': clinic_settings,
        'logo_path': logo_path,
        'for_pdf': True
    }
    
    # Generate PDF using xhtml2pdf
    try:
        from django.template.loader import render_to_string
        from xhtml2pdf import pisa
        
        # Render the same template as print view
        html_content = render_to_string('patients/assessment_print.html', context)
        
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
            filename = f'Assessment_ASM-{assessment.id:05d}_{patient.get_full_name().replace(" ", "_")}.pdf'
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        else:
            messages.error(request, 'PDF generation failed.')
            return redirect('patients:assessment_print', patient_id=patient_id, assessment_id=assessment_id)
            
    except ImportError:
        messages.error(request, 'PDF library not available. Please install xhtml2pdf.')
        return redirect('patients:assessment_print', patient_id=patient_id, assessment_id=assessment_id)
    except Exception as e:
        messages.error(request, f'PDF generation error: {str(e)}')
        return redirect('patients:assessment_print', patient_id=patient_id, assessment_id=assessment_id)


@login_required
def assessment_email_pdf(request, patient_id, assessment_id):
    """Send assessment report as PDF via email"""
    patient = get_object_or_404(Patient, patient_id=patient_id)
    assessment = get_object_or_404(Assessment, id=assessment_id, patient=patient)
    
    # Check if patient has email
    if not patient.email:
        messages.error(request, 'Patient does not have an email address on file.')
        return redirect('patients:patient_detail', patient_id=patient_id)
    
    try:
        # Get clinic settings
        try:
            clinic_settings = ClinicSettings.objects.first()
        except:
            clinic_settings = None
        
        # Build absolute logo path for PDF
        logo_path = None
        if clinic_settings and clinic_settings.logo:
            logo_path = os.path.join(settings.MEDIA_ROOT, str(clinic_settings.logo))
        
        context = {
            'patient': patient,
            'assessment': assessment,
            'clinic_settings': clinic_settings,
            'logo_path': logo_path,
            'for_pdf': True
        }
        
        # Generate PDF using xhtml2pdf
        from django.template.loader import render_to_string
        from xhtml2pdf import pisa
        
        # Render the same template as print view
        html_content = render_to_string('patients/assessment_print.html', context)
        
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
        
        if pisa_status.err:
            messages.error(request, 'PDF generation failed.')
            return redirect('patients:patient_detail', patient_id=patient_id)
        
        # Prepare email
        clinic_name = getattr(settings, 'CLINIC_NAME', 'PhysioNutrition Clinic')
        subject = f"Assessment Report - {patient.get_full_name()} from {clinic_name}"
        
        # Create email body
        email_body = f"""Dear {patient.get_full_name()},

Please find attached your {assessment.get_department_display()} assessment report from {clinic_name}.

Assessment Details:
- Type: {assessment.get_assessment_type_display()}
- Date: {assessment.assessment_date.strftime('%B %d, %Y')}
- Assessed by: {assessment.assessed_by.get_full_name() if assessment.assessed_by else 'N/A'}

If you have any questions about this assessment, please contact our clinic.

Best regards,
{clinic_name}

---
This is an automated message. Please do not reply to this email.
"""
        
        # Create email message
        email = EmailMessage(
            subject=subject,
            body=email_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[patient.email],
        )
        
        # Attach PDF
        filename = f'Assessment_ASM-{assessment.id:05d}_{patient.get_full_name().replace(" ", "_")}.pdf'
        pdf_file.seek(0)
        email.attach(filename, pdf_file.getvalue(), 'application/pdf')
        
        # Send email
        email.send()
        
        messages.success(request, f'Assessment report sent successfully to {patient.email}')
        return redirect('patients:patient_detail', patient_id=patient_id)
        
    except ImportError:
        messages.error(request, 'PDF library not available. Please install xhtml2pdf.')
        return redirect('patients:patient_detail', patient_id=patient_id)
    except Exception as e:
        messages.error(request, f'Failed to send email: {str(e)}')
        return redirect('patients:patient_detail', patient_id=patient_id)


# ── Referral Letter helpers ────────────────────────────────────────────────

def _referral_context(request, patient, assessment):
    """Build shared context for referral letter views from GET/POST params."""
    try:
        clinic_settings = ClinicSettings.objects.first()
    except Exception:
        clinic_settings = None

    params = request.POST if request.method == 'POST' else request.GET
    referred_to      = params.get('referred_to', '').strip()
    referred_to_dept = params.get('referred_to_dept', '').strip()
    urgency          = params.get('urgency', 'routine').strip()
    notes            = params.get('notes', '').strip()

    from urllib.parse import urlencode
    qs = urlencode({
        'referred_to':      referred_to,
        'referred_to_dept': referred_to_dept,
        'urgency':          urgency,
        'notes':            notes,
    })

    return {
        'patient':         patient,
        'assessment':      assessment,
        'clinic_settings': clinic_settings,
        'referred_to':      referred_to,
        'referred_to_dept': referred_to_dept,
        'urgency':          urgency,
        'notes':            notes,
        'query_string':     qs,
        'today':            date_cls.today(),
    }


@login_required
def referral_letter_print(request, patient_id, assessment_id):
    """Render referral letter for browser printing."""
    patient    = get_object_or_404(Patient, patient_id=patient_id)
    assessment = get_object_or_404(Assessment, id=assessment_id, patient=patient)
    context    = _referral_context(request, patient, assessment)
    return render(request, 'patients/referral_letter.html', context)


def _build_referral_pdf(context):
    """Generate referral letter PDF bytes. Returns (pdf_bytes, error_msg)."""
    try:
        from django.template.loader import render_to_string
        from xhtml2pdf import pisa

        logo_path = None
        cs = context.get('clinic_settings')
        if cs and cs.logo:
            logo_path = os.path.join(settings.MEDIA_ROOT, str(cs.logo))
        context = dict(context, logo_path=logo_path, for_pdf=True)

        def link_callback(uri, rel):
            if uri.startswith(('http://', 'https://')):
                return uri
            if uri.startswith(settings.MEDIA_URL):
                return os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ''))
            if uri.startswith(settings.STATIC_URL):
                return os.path.join(
                    settings.STATIC_ROOT or settings.BASE_DIR / 'static',
                    uri.replace(settings.STATIC_URL, ''),
                )
            return uri

        html = render_to_string('patients/referral_letter.html', context)
        buf  = BytesIO()
        status = pisa.CreatePDF(html, dest=buf, link_callback=link_callback)
        if status.err:
            return None, 'PDF generation failed.'
        buf.seek(0)
        return buf.getvalue(), None
    except ImportError:
        return None, 'PDF library (xhtml2pdf) not available.'
    except Exception as exc:
        return None, str(exc)


@login_required
def referral_letter_pdf(request, patient_id, assessment_id):
    """Download referral letter as PDF."""
    patient    = get_object_or_404(Patient, patient_id=patient_id)
    assessment = get_object_or_404(Assessment, id=assessment_id, patient=patient)
    context    = _referral_context(request, patient, assessment)

    pdf_bytes, err = _build_referral_pdf(context)
    if err:
        messages.error(request, err)
        return redirect('patients:referral_letter_print', patient_id=patient_id, assessment_id=assessment_id)

    filename = f'Referral_REF-{assessment.id:05d}_{patient.get_full_name().replace(" ", "_")}.pdf'
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@login_required
def referral_letter_email(request, patient_id, assessment_id):
    """Email referral letter PDF to a specified recipient."""
    patient    = get_object_or_404(Patient, patient_id=patient_id)
    assessment = get_object_or_404(Assessment, id=assessment_id, patient=patient)

    if request.method != 'POST':
        return redirect('patients:referral_letter_print', patient_id=patient_id, assessment_id=assessment_id)

    recipient_email = request.POST.get('recipient_email', '').strip()
    if not recipient_email:
        messages.error(request, 'Recipient email is required.')
        return redirect('patients:referral_letter_print', patient_id=patient_id, assessment_id=assessment_id)

    context   = _referral_context(request, patient, assessment)
    pdf_bytes, err = _build_referral_pdf(context)
    if err:
        messages.error(request, err)
        return redirect('patients:referral_letter_print', patient_id=patient_id, assessment_id=assessment_id)

    try:
        clinic_name = getattr(settings, 'CLINIC_NAME', None)
        cs = context.get('clinic_settings')
        if not clinic_name and cs:
            clinic_name = cs.clinic_name
        clinic_name = clinic_name or 'PhysioNutrition Clinic'

        referred_to = context.get('referred_to') or 'Specialist'
        subject = f'Referral Letter – {patient.get_full_name()} from {clinic_name}'
        body = (
            f'Dear {referred_to},\n\n'
            f'Please find attached a referral letter for patient {patient.get_full_name()} '
            f'(ID: {patient.patient_id}) from {assessment.get_department_display()} '
            f'at {clinic_name}.\n\n'
            f'Referring clinician: {assessment.assessed_by.get_full_name() if assessment.assessed_by else "N/A"}\n\n'
            f'Kind regards,\n{clinic_name}\n\n---\nThis is an automated message.'
        )
        email_msg = EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient_email],
        )
        filename = f'Referral_REF-{assessment.id:05d}_{patient.get_full_name().replace(" ", "_")}.pdf'
        email_msg.attach(filename, pdf_bytes, 'application/pdf')
        email_msg.send()
        messages.success(request, f'Referral letter sent to {recipient_email}.')
    except Exception as exc:
        messages.error(request, f'Failed to send email: {exc}')

    return redirect('patients:patient_detail', patient_id=patient_id)
