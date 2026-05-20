import socket
import ipaddress

def is_private(host: str) -> bool:
    try:
        ip = socket.gethostbyname(host)
        return ipaddress.ip_address(ip).is_private
    except:
        return True
