from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import HttpResponse, JsonResponse
from .models import MedicalRecord, Document
from .forms import MedicalRecordForm, DocumentForm
from patients.models import Patient
from clinic_settings.models import ClinicSettings
from .decorators import medical_staff_required, can_view_medical_records
from reports.utils import PDFReportGenerator

@login_required
def medical_record_list(request, patient_id):
    patient = get_object_or_404(Patient, patient_id=patient_id)
    
    # Check if user can view medical records
    if not can_view_medical_records(request.user):
        return render(request, 'medical_records/access_denied.html', {
            'message': 'You do not have permission to view medical records.',
            'user_role': request.user.get_role_display()
        }, status=403)
    
    records = patient.medical_records.all()
    
    # Filter by record type
    record_type = request.GET.get('type')
    if record_type:
        records = records.filter(record_type=record_type)
    
    context = {
        'patient': patient,
        'records': records,
        'medical_records': records,
        'record_types': MedicalRecord.RECORD_TYPES,
        'selected_type': record_type,
        'can_edit': request.user.role in ['doctor', 'nutritionist', 'admin'],
        'clinic_settings': ClinicSettings.get_settings(),
        'recent_documents': patient.documents.order_by('-uploaded_at')[:4],
    }
    return render(request, 'medical_records/record_list.html', context)

@medical_staff_required
def medical_record_create(request, patient_id):
    patient = get_object_or_404(Patient, patient_id=patient_id)
    
    # Check if this is an AJAX request
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if request.method == 'POST':
        form = MedicalRecordForm(request.POST, patient=patient)
        if form.is_valid():
            record = form.save(commit=False)
            record.patient = patient
            record.created_by = request.user
            record.save()
            
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'message': 'Medical record created successfully!',
                    'redirect_url': f"/medical-records/{patient.patient_id}/records/"
                })
            else:
                messages.success(request, 'Medical record created successfully!')
                return redirect('medical_records:record_list', patient_id=patient.patient_id)
        else:
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                }, status=400)
    else:
        form = MedicalRecordForm(patient=patient)
    
    if is_ajax:
        # Return form HTML for modal
        from django.template.loader import render_to_string
        html = render_to_string('medical_records/record_create_modal.html', {
            'form': form,
            'patient': patient
        }, request=request)
        return JsonResponse({'html': html})
    
    context = {
        'form': form,
        'patient': patient,
    }
    return render(request, 'medical_records/record_create.html', context)

@medical_staff_required
def medical_record_edit(request, pk):
    record = get_object_or_404(MedicalRecord, pk=pk)
    patient = record.patient
    
    # Check if this is an AJAX request
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if request.method == 'POST':
        form = MedicalRecordForm(request.POST, instance=record, patient=patient)
        if form.is_valid():
            form.save()
            
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'message': 'Medical record updated successfully!',
                    'redirect_url': f"/medical-records/{patient.patient_id}/records/"
                })
            else:
                messages.success(request, 'Medical record updated successfully!')
                return redirect('medical_records:record_list', patient_id=patient.patient_id)
        else:
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                }, status=400)
    else:
        form = MedicalRecordForm(instance=record, patient=patient)
    
    if is_ajax:
        # Return form HTML for modal
        from django.template.loader import render_to_string
        html = render_to_string('medical_records/record_edit_modal.html', {
            'form': form,
            'patient': patient,
            'record': record
        }, request=request)
        return JsonResponse({'html': html})
    
    context = {
        'form': form,
        'patient': patient,
        'record': record,
    }
    return render(request, 'medical_records/record_edit.html', context)

@login_required
def medical_record_detail(request, pk):
    record = get_object_or_404(MedicalRecord, pk=pk)
    
    # Check if user can view medical records
    if not can_view_medical_records(request.user):
        return render(request, 'medical_records/access_denied.html', {
            'message': 'You do not have permission to view medical records.',
            'user_role': request.user.get_role_display()
        }, status=403)
    
    context = {
        'record': record,
        'can_edit': request.user.role in ['doctor', 'nutritionist', 'admin'],
    }
    return render(request, 'medical_records/record_detail.html', context)


@login_required
def medical_record_print(request, patient_id):
    patient = get_object_or_404(Patient, patient_id=patient_id)

    if not can_view_medical_records(request.user):
        return render(request, 'medical_records/access_denied.html', {
            'message': 'You do not have permission to view medical records.',
            'user_role': request.user.get_role_display()
        }, status=403)

    clinic_settings = ClinicSettings.get_settings()
    records = patient.medical_records.select_related('created_by', 'appointment').all()
    documents = patient.documents.select_related('uploaded_by').order_by('-uploaded_at').all()
    vital_signs = patient.vital_signs.select_related('recorded_by').order_by('-recorded_date')
    triages = patient.triages.select_related('triaged_by').order_by('-triage_date')
    assessments = patient.assessments.select_related('assessed_by').order_by('-assessment_date')
    selected_record_id = request.GET.get('record')

    record_counts = list(
        records.values('record_type').annotate(total=Count('id')).order_by('record_type')
    )

    record_creators = []
    for creator in (
        records.exclude(created_by__isnull=True)
        .values('created_by__first_name', 'created_by__last_name')
        .distinct()
    ):
        first = creator.get('created_by__first_name') or ''
        last = creator.get('created_by__last_name') or ''
        full_name = f"{first} {last}".strip()
        if full_name:
            record_creators.append(full_name)

    context = {
        'patient': patient,
        'medical_records': records,
        'documents': documents,
        'clinic_settings': clinic_settings,
        'selected_record_id': selected_record_id,
        'record_counts': record_counts,
        'record_creators': record_creators,
        'latest_record': records.first(),
        'earliest_record': records.last(),
        'vital_signs': vital_signs,
        'triages': triages,
        'assessments': assessments,
    }

    return render(request, 'medical_records/record_print.html', context)


@login_required
def medical_record_print_pdf(request, patient_id):
    """Generate and download medical records as PDF using same template as print view"""
    patient = get_object_or_404(Patient, patient_id=patient_id)

    if not can_view_medical_records(request.user):
        return render(request, 'medical_records/access_denied.html', {
            'message': 'You do not have permission to view medical records.',
            'user_role': request.user.get_role_display()
        }, status=403)

    # Get all medical records and related data
    medical_records = patient.medical_records.select_related('created_by', 'appointment').order_by('-created_at')
    documents = patient.documents.select_related('uploaded_by').order_by('-uploaded_at')
    
    # Get statistics
    record_creators = medical_records.values_list('created_by__first_name', 'created_by__last_name').distinct()
    record_creators = [f"{first} {last}" for first, last in record_creators if first]
    
    earliest_record = medical_records.order_by('created_at').first()
    latest_record = medical_records.order_by('-created_at').first()
    
    # Get record type counts
    from django.db.models import Count
    record_counts = medical_records.values('record_type').annotate(total=Count('id'))
    
    # Get clinic settings
    try:
        from clinic_settings.models import ClinicSettings
        clinic_settings = ClinicSettings.objects.first()
    except:
        clinic_settings = None
    
    # Build absolute logo path for PDF
    import os
    from django.conf import settings
    logo_path = None
    if clinic_settings and clinic_settings.logo:
        logo_path = os.path.join(settings.MEDIA_ROOT, str(clinic_settings.logo))
    
    context = {
        'patient': patient,
        'medical_records': medical_records,
        'documents': documents,
        'record_creators': record_creators,
        'earliest_record': earliest_record,
        'latest_record': latest_record,
        'record_counts': record_counts,
        'selected_record_id': request.GET.get('record_id'),
        'clinic_settings': clinic_settings,
        'logo_path': logo_path,
        'for_pdf': True
    }
    
    # Generate PDF using xhtml2pdf
    try:
        from django.template.loader import render_to_string
        from xhtml2pdf import pisa
        from io import BytesIO
        
        # Render the same template as print view
        html_content = render_to_string('medical_records/record_print.html', context)
        
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
            filename = f'Medical_Records_{patient.patient_id}_{patient.get_full_name().replace(" ", "_")}.pdf'
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        else:
            messages.error(request, 'PDF generation failed.')
            return redirect('medical_records:record_print', patient_id=patient_id)
            
    except ImportError:
        messages.error(request, 'PDF library not available. Please install xhtml2pdf.')
        return redirect('medical_records:record_print', patient_id=patient_id)
    except Exception as e:
        messages.error(request, f'PDF generation error: {str(e)}')
        return redirect('medical_records:record_print', patient_id=patient_id)

@login_required
def document_list(request, patient_id):
    patient = get_object_or_404(Patient, patient_id=patient_id)
    documents = patient.documents.all()
    
    # Filter by document type
    doc_type = request.GET.get('type')
    if doc_type:
        documents = documents.filter(document_type=doc_type)
    
    context = {
        'patient': patient,
        'documents': documents,
        'document_types': Document.DOCUMENT_TYPES,
        'selected_type': doc_type,
    }
    return render(request, 'medical_records/document_list.html', context)

@medical_staff_required
def document_upload(request, patient_id):
    patient = get_object_or_404(Patient, patient_id=patient_id)
    
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.patient = patient
            document.uploaded_by = request.user
            document.save()
            messages.success(request, 'Document uploaded successfully!')
            return redirect('medical_records:document_list', patient_id=patient.patient_id)
    else:
        form = DocumentForm()
    
    context = {
        'form': form,
        'patient': patient,
    }
    return render(request, 'medical_records/document_upload.html', context)

@login_required
def single_record_print(request, record_id):
    """Print view for a single medical record"""
    from django.utils import timezone
    
    record = get_object_or_404(MedicalRecord, pk=record_id)
    patient = record.patient
    clinic_settings = ClinicSettings.get_settings()
    
    # Check if user can view medical records
    if not can_view_medical_records(request.user):
        return render(request, 'medical_records/access_denied.html', {
            'message': 'You do not have permission to view medical records.',
            'user_role': request.user.get_role_display()
        }, status=403)
    
    context = {
        'record': record,
        'patient': patient,
        'clinic_settings': clinic_settings,
        'now': timezone.now(),
    }
    
    return render(request, 'medical_records/medical_record_print.html', context)
