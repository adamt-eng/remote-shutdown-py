import http.server
import socketserver
import subprocess
import socket
from urllib.parse import urlparse, parse_qs
import winreg as reg 
import os
import sys

PORT_NUMBER = 5555
TOKEN = "YOUR_TOKEN_HERE"

def get_local_ipv4_address():
    """Get the local IPv4 address."""
    try:
        # Create a socket to get the local IP address
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))  # Google's public DNS server
            local_ip = s.getsockname()[0]
        return local_ip
    except Exception as e:
        print(f"Error getting local IP address: {e}")
        return "127.0.0.1"

class RemoteShutdownHandler(http.server.BaseHTTPRequestHandler):
    def send_response_message(self, status_code, message):
        """Helper method to send response with a message."""
        self.send_response(status_code)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(f"<html><body>{message}</body></html>".encode())

    def do_GET(self):
        """Handle GET requests."""
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        
        print(f"Request received: {self.path}")
        
        if "shutdown" in query_params and query_params["shutdown"][0] == "true" and \
           "token" in query_params and query_params["token"][0] == TOKEN:
            self.send_response_message(200, "Shutting down...")
            subprocess.run(["shutdown", "-s", "-f", "-t", "0"], shell=True)
        else:
            self.send_response_message(400, "Invalid request.")

def run_server():
    """Run the HTTP server to listen for shutdown requests."""
    local_ip = get_local_ipv4_address()
    url = f"http://{local_ip}:{PORT_NUMBER}/"
    print(f"Listening for shutdown requests at {url}")

    with socketserver.TCPServer(("", PORT_NUMBER), RemoteShutdownHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer is shutting down...")
            httpd.shutdown()

def add_to_registry():
    path_to_script = os.path.dirname(os.path.realpath(__file__))
    script_name = "remote-shutdown.py"    
    script_path = os.path.join(path_to_script, script_name)
    
    open = reg.OpenKey(reg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, reg.KEY_ALL_ACCESS)
    reg.SetValueEx(open, "RemoteShutdown", 0, reg.REG_SZ, f'"{sys.executable}" "{script_path}"')
    reg.CloseKey(open)

if __name__ == "__main__":
    add_to_registry()
    run_server()
