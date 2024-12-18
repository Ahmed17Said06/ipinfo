from django.test import TestCase

# Create your tests here.
from celery import shared_task
import requests
from ipinfo.utils import is_valid_ip

@shared_task
def process_ips(ips):
    results = []
    for ip in ips:
        if is_valid_ip(ip):  # Double-check validity here
            response = requests.get(f"https://ipinfo.io/{ip}/json")
            if response.status_code == 200:
                data = response.json()
                results.append({
                    "ip": ip,
                    "info": data
                })
            else:
                results.append({"ip": ip, "error": "Could not retrieve info"})
        else:
            results.append({"ip": ip, "error": "Invalid IP"})
    return results
