from django.urls import path
from . import views

app_name = 'patients'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('list/', views.patient_list, name='patient_list'),
    path('register/', views.patient_register, name='patient_register'),
    path('register/visiting/', views.visiting_patient_register, name='visiting_patient_register'),
    path('<str:patient_id>/', views.patient_detail, name='patient_detail'),
    path('<int:pk>/update/', views.PatientUpdateView.as_view(), name='patient_update'),
    path('<str:patient_id>/print/', views.patient_details_print, name='patient_details_print'),
    path('<str:patient_id>/vitals/', views.record_vitals, name='record_vitals'),
    path('patient/<str:patient_id>/triage/', views.triage_patient, name='triage_patient'),
    path('patient/<str:patient_id>/assessment/', views.assessment_create, name='assessment_create'),
    path('patient/<str:patient_id>/physiotherapy-assessment/', views.physiotherapy_assessment, name='physiotherapy_assessment'),
    path('patient/<str:patient_id>/nutrition-assessment/', views.nutrition_assessment, name='nutrition_assessment'),
    path('<str:patient_id>/triage-assessment/', views.triage_assessment, name='triage_assessment'),  # Legacy URL
    path('<str:patient_id>/medical-records/', views.patient_medical_records, name='patient_medical_records'),
    
    # Assessment print and PDF
    path('<str:patient_id>/assessment/<int:assessment_id>/print/', views.assessment_print, name='assessment_print'),
    path('<str:patient_id>/assessment/<int:assessment_id>/pdf/', views.assessment_print_pdf, name='assessment_print_pdf'),
    path('<str:patient_id>/assessment/<int:assessment_id>/email/', views.assessment_email_pdf, name='assessment_email_pdf'),
    path('<str:patient_id>/assessment/<int:assessment_id>/edit/', views.assessment_update, name='assessment_update'),

    # Referral letter (print / PDF / email)
    path('<str:patient_id>/assessment/<int:assessment_id>/referral/', views.referral_letter_print, name='referral_letter_print'),
    path('<str:patient_id>/assessment/<int:assessment_id>/referral/pdf/', views.referral_letter_pdf, name='referral_letter_pdf'),
    path('<str:patient_id>/assessment/<int:assessment_id>/referral/email/', views.referral_letter_email, name='referral_letter_email'),
    
    # Vital Signs print
    path('<str:patient_id>/vitals/<int:vital_id>/print/', views.vital_signs_print, name='vital_signs_print'),
    
    # Medical Info print
    path('<str:patient_id>/medical-info/print/', views.medical_info_print, name='medical_info_print'),
    
    # AJAX-only assessment endpoints
    path('ajax/patient/<str:patient_id>/physiotherapy-assessment/', views.physiotherapy_assessment_ajax, name='physiotherapy_assessment_ajax'),
    path('ajax/patient/<str:patient_id>/nutrition-assessment/', views.nutrition_assessment_ajax, name='nutrition_assessment_ajax'),
    path('ajax/patient/<str:patient_id>/general-assessment/', views.general_assessment_ajax, name='general_assessment_ajax'),
    
    # AJAX-only vital signs and triage endpoints
    path('ajax/<str:patient_id>/vitals/', views.vital_signs_record_ajax, name='vital_signs_record_ajax'),
    path('ajax/<str:patient_id>/triage/', views.triage_create_ajax, name='triage_create_ajax'),
    
    # Physiotherapist dashboard
    path('physiotherapist/my-patients/', views.physiotherapist_patients, name='physiotherapist_patients'),
    
    # Nutritionist dashboard
    path('nutritionist/my-patients/', views.nutritionist_patients, name='nutritionist_patients'),
]
