
# 1.1.1.1, 8.8.8.8, 90.56.47.100,222.186.13.131 ,218.92.0.76 ,196.242.178.111 ,115.79.87.21, 14.241.110.89, 8.208.9.11 ,198.235.24.226 ,193.3.53.3

from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import JsonResponse, StreamingHttpResponse
import json
from ipinfo.tasks import process_ip
from ipinfo.utils import is_valid_ip
import time


def event_stream(task_ids):
    """
    Stream results for each IP as they are processed.
    """
    for task_id in task_ids:
        task_result = process_ip.AsyncResult(task_id)

        # Polling while the task is not ready
        while not task_result.ready():
            # Optionally sleep to reduce CPU usage
            time.sleep(0.1)

        # Once the task is finished, yield its result to the client
        result = task_result.result
        if isinstance(result, dict):
            yield f"data: {json.dumps(result)}\n\n"
        else:
            yield f"data: {json.dumps({'error': 'Invalid result format'})}\n\n"

def get_task_result(request, task_id):
    """
    Return the result of a specific task as a Server-Sent Event stream.
    """
    return StreamingHttpResponse(event_stream([task_id]), content_type='text/event-stream')

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
                # Submit each valid IP as a Celery task and collect task IDs
                task_ids = []
                for ip in valid_ips:
                    task_result = process_ip.delay(ip)
                    task_ids.append(task_result.id)

                return JsonResponse({"status": "success", "task_ids": task_ids})
            else:
                return JsonResponse({"status": "error", "message": "No valid IPs submitted."})
        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON payload."}, status=400)
        
    elif request.method == 'GET':
        return render(request, "submit_ips.html")  # Render the form for GET request

    return JsonResponse({"status": "error", "message": "Invalid request method."}, status=405)