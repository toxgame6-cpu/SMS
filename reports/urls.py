from django.urls import path
from . import views

urlpatterns = [
    path('reports/', views.reports_dashboard, name='reports_dashboard'),
    path('reports/export-pdf/', views.export_summary_pdf, name='export_summary_pdf'),
]