from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import JsonResponse, StreamingHttpResponse
import json
from ipinfo.tasks import process_ip
from ipinfo.utils import is_valid_ip
import redis
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_client = redis.StrictRedis.from_url(REDIS_URL)

def event_stream(task_ids):
    pubsub = redis_client.pubsub()
    pubsub.subscribe('ip_results')

    for message in pubsub.listen():
        if message['type'] == 'message':
            result = json.loads(message['data'])
            yield f"data: {json.dumps(result)}\n\n"

@csrf_exempt
def submit_ips(request):
    if request.method == 'POST':
        try:
            # Parse JSON payload
            data = json.loads(request.body)
            ips = data.get('ips', [])

            # Validate IPs
            valid_ips = [ip for ip in ips if is_valid_ip(ip)]
            invalid_ips = [ip for ip in ips if not is_valid_ip(ip)]

            if valid_ips:
                task_ids = []
                for ip in valid_ips:
                    task_result = process_ip.delay(ip)
                    task_ids.append(task_result.id)

                response_data = {"status": "success", "task_ids": task_ids}
                if invalid_ips:
                    response_data["invalid_ips"] = invalid_ips

                return JsonResponse(response_data)
            else:
                return JsonResponse({"status": "error", "message": "No valid IPs provided.", "invalid_ips": invalid_ips})
        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON payload."})
        
    elif request.method == 'GET':
        return render(request, "submit_ips.html")  # Render the form for GET request
    
    return JsonResponse({"status": "error", "message": "Invalid request method."})

def stream_view(request):
    task_ids = request.GET.getlist('task_ids')  # List of task IDs to stream
    response = StreamingHttpResponse(event_stream(task_ids), content_type='text/event-stream')
    return response

def get_task_result(request, task_id):
    task_result = process_ip.AsyncResult(task_id)
    if task_result.state == 'PENDING':
        response = {
            'state': task_result.state,
            'current': 0,
            'total': 1,
            'status': 'Pending...'
        }
    elif task_result.state != 'FAILURE':
        response = {
            'state': task_result.state,
            'current': task_result.info.get('current', 0),
            'total': task_result.info.get('total', 1),
            'status': task_result.info.get('status', ''),
            'result': task_result.info.get('results', [])
        }
        if 'result' in task_result.info:
            response['result'] = task_result.info['result']
    else:
        # something went wrong in the background job
        response = {
            'state': task_result.state,
            'current': 1,
            'total': 1,
            'status': str(task_result.info),  # this is the exception raised
        }
    return JsonResponse(response)