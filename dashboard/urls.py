 
from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard_redirect, name='dashboard_redirect'),
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('hod-panel/', views.hod_dashboard, name='hod_dashboard'),
    path('teacher-panel/', views.teacher_dashboard, name='teacher_dashboard'),
    path('guardian-panel/', views.guardian_dashboard, name='guardian_dashboard'),
]