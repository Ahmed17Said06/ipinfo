import aiohttp
import asyncio
from celery import shared_task
from ipinfo.utils import is_valid_ip

@shared_task
def process_ips(ips):
    # This function should not be async, so we use asyncio.run() to run the async logic
    return asyncio.run(process_ips_async(ips))

async def process_ips_async(ips):
    results = []
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        
        for ip in ips:
            if is_valid_ip(ip):  # Double-check validity here
                # Create an async task for the HTTP request
                task = fetch_ip_info(session, ip)
                tasks.append(task)
            else:
                results.append({"ip": ip, "error": "Invalid IP"})
        
        # Wait for all async tasks to complete and gather the results
        responses = await asyncio.gather(*tasks)
        
        for response in responses:
            results.append(response)
    
    return results

async def fetch_ip_info(session, ip):
    try:
        async with session.get(f"https://ipinfo.io/{ip}/json") as response:
            if response.status == 200:
                data = await response.json()
                return {"ip": ip, "info": data}
            else:
                return {"ip": ip, "error": "Could not retrieve info"}
    except Exception as e:
        return {"ip": ip, "error": f"Request failed: {str(e)}"}
