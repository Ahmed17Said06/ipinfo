from celery import shared_task
import aiohttp
import os
from ipinfo.utils import is_valid_ip
import traceback
import redis
import json
from asgiref.sync import async_to_sync

BASE_URL = os.getenv("IPINFO_API_URL", "https://ipinfo.io")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_client = redis.StrictRedis.from_url(REDIS_URL)

@shared_task(bind=True)
def process_ips(self, ips):
    results = []
    for ip in ips:
        if is_valid_ip(ip):
            try:
                ip_result = async_to_sync(process_ip)(ip)
                results.append(ip_result)
                redis_client.publish('ip_results', json.dumps(ip_result))
            except Exception as e:
                error_result = {"ip": ip, "error": str(e)}
                results.append(error_result)
                redis_client.publish('ip_results', json.dumps(error_result))
        else:
            error_result = {"ip": ip, "error": "Invalid IP"}
            results.append(error_result)
            redis_client.publish('ip_results', json.dumps(error_result))
    return results

@shared_task(bind=True)
def process_ip(self, ip):
    """
    Fetch information for a single IP address asynchronously.
    """
    try:
        result = async_to_sync(fetch_ip_info)(ip)
        redis_client.publish('ip_results', json.dumps(result))
        return result
    except Exception as e:
        # Log the error with traceback for debugging
        error_message = f"Error processing IP {ip}: {str(e)}"
        traceback_details = traceback.format_exc()
        error_result = {
            "ip": ip,
            "error": error_message,
            "traceback": traceback_details,
        }
        redis_client.publish('ip_results', json.dumps(error_result))
        return error_result

async def fetch_ip_info(ip):
    """
    Fetch information about an IP address using aiohttp asynchronously.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/{ip}/json") as response:
                if response.status == 200:
                    data = await response.json()
                    return {"ip": ip, "info": data}
                else:
                    return {"ip": ip, "error": f"HTTP {response.status}"}
    except Exception as e:
        return {"ip": ip, "error": str(e)}
