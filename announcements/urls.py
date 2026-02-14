from django.urls import path
from . import views

urlpatterns = [
    path('announcements/', views.announcement_list, name='announcement_list'),
    path('announcements/create/', views.announcement_create, name='announcement_create'),
    path('announcements/<int:pk>/', views.announcement_detail, name='announcement_detail'),
    path('announcements/<int:pk>/edit/', views.announcement_edit, name='announcement_edit'),
    path('announcements/<int:pk>/delete/', views.announcement_delete, name='announcement_delete'),
    path('announcements/<int:pk>/toggle-pin/', views.announcement_toggle_pin, name='announcement_toggle_pin'),
    path('announcements/mark-all-read/', views.mark_all_announcements_read, name='mark_all_announcements_read'),
]