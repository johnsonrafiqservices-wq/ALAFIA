from django.urls import path
from . import views

app_name = 'medical_records'

urlpatterns = [
    path('<str:patient_id>/records/', views.medical_record_list, name='record_list'),
    path('<str:patient_id>/records/create/', views.medical_record_create, name='record_create'),
    path('<str:patient_id>/records/print/', views.medical_record_print, name='record_print'),
    path('<str:patient_id>/records/print/pdf/', views.medical_record_print_pdf, name='record_print_pdf'),
    path('records/<int:pk>/', views.medical_record_detail, name='record_detail'),
    path('records/<int:pk>/edit/', views.medical_record_edit, name='record_edit'),
    path('records/<int:record_id>/print/', views.single_record_print, name='single_record_print'),
    path('<str:patient_id>/documents/', views.document_list, name='document_list'),
    path('<str:patient_id>/documents/upload/', views.document_upload, name='document_upload'),
]
