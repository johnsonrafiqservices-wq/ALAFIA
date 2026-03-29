from django.urls import path
from . import views

app_name = 'clinic_settings'

urlpatterns = [
    path('', views.clinic_settings_view, name='settings'),
    path('theme/', views.theme_customization_view, name='theme_customization'),
]
