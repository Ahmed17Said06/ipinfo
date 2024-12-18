import re

# Function to validate IP addresses
def is_valid_ip(ip):
    ip_pattern = re.compile(
        r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"
    )
    return re.match(ip_pattern, ip)