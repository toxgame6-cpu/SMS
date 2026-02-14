 
from django.urls import path
from . import views

urlpatterns = [
    path('teachers/', views.teacher_list, name='teacher_list'),
    path('teachers/create/', views.staff_create, {'staff_type': 'teacher'}, name='teacher_create'),
    path('teachers/<int:pk>/edit/', views.staff_edit, {'staff_type': 'teacher'}, name='teacher_edit'),
    path('teachers/<int:pk>/delete/', views.staff_delete, {'staff_type': 'teacher'}, name='teacher_delete'),
    path('teachers/<int:pk>/', views.staff_detail, {'staff_type': 'teacher'}, name='teacher_detail'),

    path('guardians/', views.guardian_list, name='guardian_list'),
    path('guardians/create/', views.staff_create, {'staff_type': 'guardian'}, name='guardian_create'),
    path('guardians/<int:pk>/edit/', views.staff_edit, {'staff_type': 'guardian'}, name='guardian_edit'),
    path('guardians/<int:pk>/delete/', views.staff_delete, {'staff_type': 'guardian'}, name='guardian_delete'),
    path('guardians/<int:pk>/', views.staff_detail, {'staff_type': 'guardian'}, name='guardian_detail'),

    path('hods/', views.hod_list, name='hod_list'),
    path('hods/create/', views.staff_create, {'staff_type': 'hod'}, name='hod_create'),
    path('hods/<int:pk>/edit/', views.staff_edit, {'staff_type': 'hod'}, name='hod_edit'),
    path('hods/<int:pk>/delete/', views.staff_delete, {'staff_type': 'hod'}, name='hod_delete'),
    path('hods/<int:pk>/', views.staff_detail, {'staff_type': 'hod'}, name='hod_detail'),
]