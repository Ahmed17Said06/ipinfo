# ipinfo_project/ipinfo/utils.py
import re

# Validate IP addresses
def is_valid_ip(ip):
    if not ip: 
        return False
    ip_pattern = re.compile(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")
    if re.match(ip_pattern, ip):
        octets = ip.split('.')
        return all(0 <= int(octet) <= 255 for octet in octets)
    return False
