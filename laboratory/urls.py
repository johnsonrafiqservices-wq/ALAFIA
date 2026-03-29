from django.urls import path
from . import views

app_name = 'laboratory'

urlpatterns = [
    path('', views.labtest_list, name='labtest_list'),
    path('add/', views.labtest_add, name='labtest_add'),
    path('request/', views.labtest_request, name='labtest_request'),
    path('results/', views.labtest_results, name='labtest_results'),
    path('result/add/', views.labtest_result_add, name='labtest_result_add'),
]
