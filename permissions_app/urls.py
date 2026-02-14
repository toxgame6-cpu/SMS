 
from django.urls import path
from . import views

urlpatterns = [
    path('permissions/', views.permission_list, name='permission_list'),
    path('permissions/save/<int:user_id>/', views.permission_save, name='permission_save'),
]