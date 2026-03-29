from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    path('', views.billing_dashboard, name='billing_dashboard'),
    
    # Invoice URLs
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoices/create/', views.invoice_create, name='invoice_create'),
    path('invoices/create-for-patient/', views.invoice_create_for_patient, name='invoice_create_for_patient'),
    path('invoices/<int:pk>/', views.invoice_detail, name='invoice_detail'),
    path('invoices/<int:pk>/edit/', views.invoice_edit, name='invoice_edit'),
    path('invoices/<int:pk>/pdf/', views.invoice_pdf, name='invoice_pdf'),
    path('invoices/<int:pk>/print/', views.invoice_print, name='invoice_print'),
    path('invoices/<int:pk>/status/', views.invoice_status_update, name='invoice_status_update'),
    path('invoices/bulk-action/', views.bulk_invoice_action, name='bulk_invoice_action'),
    path('invoices/aging-report/', views.invoice_aging_report, name='invoice_aging_report'),
    path('patients/<str:patient_id>/draft-invoices/', views.patient_draft_invoices, name='patient_draft_invoices'),
    path('invoices/<int:pk>/send-email/', views.send_invoice_email, name='invoice_send_email'),
    
    # Payment URLs
    path('payments/create/', views.payment_create, name='payment_create'),
    path('invoices/<int:invoice_pk>/payment/', views.payment_create, name='payment_create_for_invoice'),
    path('payments/', views.payment_list, name='payment_list'),
    path('payments/<int:pk>/', views.payment_detail, name='payment_detail'),
    path('payments/<int:pk>/receipt/', views.payment_receipt, name='payment_receipt'),
    path('payments/<int:pk>/receipt/pdf/', views.payment_receipt_pdf, name='payment_receipt_pdf'),
    path('payments/<int:pk>/send-email/', views.send_payment_receipt_email, name='payment_send_email'),
    
    # Insurance Claim URLs
    path('claims/create/', views.insurance_claim_create, name='insurance_claim_create'),
    path('invoices/<int:invoice_pk>/claim/', views.insurance_claim_create, name='insurance_claim_create_for_invoice'),
    path('claims/', views.insurance_claim_list, name='insurance_claim_list'),
    path('claims/<int:pk>/print/', views.insurance_claim_print, name='insurance_claim_print'),
    
    # Payment Plan URLs
    path('payment-plans/', views.payment_plan_list, name='payment_plan_list'),
    path('invoices/<int:invoice_pk>/payment-plan/', views.payment_plan_create, name='payment_plan_create'),
    path('payment-plans/<int:pk>/', views.payment_plan_detail, name='payment_plan_detail'),
    
    # AJAX URLs
    path('ajax/invoices/create-full/', views.invoice_create_full_ajax, name='invoice_create_full_ajax'),
    path('ajax/invoices/create/', views.invoice_create_ajax, name='invoice_create_ajax'),
    path('api/service-price/', views.get_service_price, name='get_service_price'),
    path('ajax/payment/record/', views.payment_record_ajax, name='payment_record_ajax'),
    path('ajax/invoices/for-patient/', views.invoices_for_patient_ajax, name='invoices_for_patient_ajax'),
    path('debug/payment/', views.payment_debug, name='payment_debug'),
    path('test/payment/', views.payment_test, name='payment_test'),
]
