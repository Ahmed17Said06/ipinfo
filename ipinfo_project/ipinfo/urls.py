# ipinfo/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('submit-ips/', views.submit_ips, name='submit_ips'),
]
