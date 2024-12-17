from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import JsonResponse
import re

# Create your views here.

# Function to validate IP addresses
def is_valid_ip(ip):
    ip_pattern = re.compile(
        r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"
    )
    return re.match(ip_pattern, ip)

@csrf_exempt 
def submit_ips(request):
    if request.method == 'POST':
        ip_list = request.POST.getlist('ips')  # Expecting a list of IPs
        invalid_ips = [ip for ip in ip_list if not is_valid_ip(ip)]

        if invalid_ips:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid IPs found',
                'invalid_ips': invalid_ips
            }, status=400)
        

        # Add logic to process the IPs with Celery (to be added in the next step)
        return JsonResponse({
            'status': 'success',
            'message': 'IPs submitted successfully',
            'ips': ip_list
        })

    return JsonResponse({
        'status': 'error',
        'message': 'Only POST requests are allowed.'
    }, status=405)