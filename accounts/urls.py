from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.custom_logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('password-change/', views.CustomPasswordChangeView.as_view(), name='password_change'),
    path('permissions/', views.user_permissions_list, name='user_permissions_list'),
    path('permissions/<int:user_id>/edit/', views.edit_user_permissions, name='edit_user_permissions'),
]
