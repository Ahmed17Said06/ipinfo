from celery import shared_task, Celery
import aiohttp
import os
from asgiref.sync import async_to_sync
from ipinfo.utils import is_valid_ip
import traceback


BASE_URL = os.getenv("IPINFO_API_URL", "https://ipinfo.io")

@shared_task(bind=True)
def process_ips(self, ips):
    """
    Process a list of IPs one by one and send updates incrementally.
    This task handles each IP synchronously to stream updates to the frontend.
    """
    results = []
    for ip in ips:
        if is_valid_ip(ip):
            # Trigger the `process_ip` task for each IP and wait for completion
            ip_result = process_ip.apply(args=[ip])
            results.append(ip_result.result)

            # Update task state incrementally to send progress updates
            self.update_state(
                state='PROGRESS',
                meta={"current": len(results), "total": len(ips), "results": results}
            )
        else:
            results.append({"ip": ip, "error": "Invalid IP"})
            self.update_state(
                state='PROGRESS',
                meta={"current": len(results), "total": len(ips), "results": results}
            )
    return results

@shared_task(bind=True)
def process_ip(self, ip):
    """
    Fetch information for a single IP address.
    """
    try:
        # Run the async function synchronously
        result = async_to_sync(fetch_ip_info)(ip)
        return result
    except Exception as e:
        # Log the error with traceback for better debugging
        error_message = f"Error processing IP {ip}: {str(e)}"
        traceback_details = traceback.format_exc()
        return {
            "ip": ip,
            "error": error_message,
            "traceback": traceback_details,
        }


async def fetch_ip_info(ip):
    """
    Fetch information about an IP address using aiohttp.
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
        return {"ip": ip, "error": f"Request failed: {str(e)}"}
