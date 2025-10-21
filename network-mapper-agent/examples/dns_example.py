# Example: DNS lookups
import socket

# DNS lookup
ip = socket.gethostbyname('google.com')
print(f"Google IP: {ip}")

addrinfo = socket.getaddrinfo('example.com', 80)
print(f"Addrinfo: {addrinfo}")
