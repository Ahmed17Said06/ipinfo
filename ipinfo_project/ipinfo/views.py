from django.views.decorators.csrf import csrf_exempt
import json
from django.shortcuts import render
from django.http import JsonResponse
from ipinfo.tasks import process_ips
from ipinfo.utils import is_valid_ip

# Create your views here.
@csrf_exempt
def submit_ips(request):
    if request.method == 'POST':
        try:
            # Parse JSON payload
            data = json.loads(request.body)
            ips = data.get('ips', [])


            # Validate IPs
            valid_ips = [ip for ip in ips if is_valid_ip(ip)]

            if valid_ips:
                process_ips.delay(valid_ips)  # Add valid IPs to the Celery task queue
                return JsonResponse({"status": "success", "message": "IPs submitted successfully", "ips": valid_ips})

            return JsonResponse({"status": "error", "message": "No valid IPs submitted."})
        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON payload."}, status=400)
        
    elif request.method == 'GET':
        return render(request, "submit_ips.html")
    
    return JsonResponse({"status": "error", "message": "Invalid request method."}, status=405)
