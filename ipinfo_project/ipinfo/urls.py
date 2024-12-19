# /ipinfo_project/ipinfo/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('submit-ips/', views.submit_ips, name='submit_ips'),
    path('task_result/<task_id>/', views.get_task_result, name='task_result'),  # Keep only this
]
