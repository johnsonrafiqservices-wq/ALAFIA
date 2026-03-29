from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.reports_dashboard, name='reports_dashboard'),
    path('statistics/', views.statistics, name='statistics'),
    path('statistics/export/excel/', views.export_statistics_excel, name='export_statistics_excel'),
    path('patients/', views.patient_reports, name='patient_reports'),
    path('financial/', views.financial_reports, name='financial_reports'),
    path('appointments/', views.appointment_report, name='appointment_report'),
    path('export/', views.export_report, name='export_report'),
    path('audit/', views.audit_log, name='audit_log'),
    path('performance/', views.report_performance, name='report_performance'),
    path('physiotherapy/', views.physiotherapy_reports, name='physiotherapy_reports'),
    path('nutrition/', views.nutrition_reports, name='nutrition_reports'),
    path('clinical-summary/', views.clinical_summary_report, name='clinical_summary_report'),
]
