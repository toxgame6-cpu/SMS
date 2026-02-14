from django.urls import path
from . import views

urlpatterns = [
    path('files/', views.file_list, name='file_list'),
    path('files/upload/', views.upload_excel, name='upload_excel'),
    path('files/<int:file_id>/', views.student_list, name='student_list'),
    path('files/<int:file_id>/delete/', views.file_delete, name='file_delete'),
    path('files/<int:file_id>/download/', views.file_download, name='file_download'),
    path('my-files/', views.my_assigned_files, name='my_assigned_files'),
    path('students/<int:pk>/', views.student_profile, name='student_profile'),
    path('students/<int:pk>/edit/', views.student_edit, name='student_edit'),
    path('students/<int:pk>/delete/', views.student_delete, name='student_delete'),
    path('students/<int:pk>/pdf/', views.student_pdf, name='student_pdf'),
]