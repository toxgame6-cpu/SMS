from django.urls import path
from . import views

urlpatterns = [
    path('notifications/', views.notification_list, name='notification_list'),
    path('my-requests/', views.my_requests, name='my_requests'),
    path('notifications/mark-edit/', views.create_mark_edit, name='create_mark_edit'),
    path('notifications/<int:pk>/resolve/', views.resolve_notification, name='resolve_notification'),
    path('notifications/<int:pk>/dismiss/', views.dismiss_notification, name='dismiss_notification'),
    path('notifications/mark-all-read/', views.mark_all_read, name='mark_all_read'),
    # Activity Feed
    path('activity/', views.activity_feed, name='activity_feed'),
    path('activity/<int:pk>/read/', views.mark_activity_read, name='mark_activity_read'),
    path('activity/mark-all-read/', views.mark_all_activities_read, name='mark_all_activities_read'),
]