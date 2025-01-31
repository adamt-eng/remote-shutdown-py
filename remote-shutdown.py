import http.server
import socketserver
import subprocess
import socket
from urllib.parse import urlparse, parse_qs
import winreg as reg 
import os
import sys
from pathlib import Path

PORT_NUMBER = 5555
TOKEN = "YOUR_TOKEN_HERE"

# Check if running with pythonw.exe
IS_RUNNING_WITH_PYTHONW = sys.executable.lower().endswith("pythonw.exe")

# Redirect output to a log file when using pythonw.exe
if IS_RUNNING_WITH_PYTHONW:
    log_file = os.path.join(os.path.dirname(__file__), "remote-shutdown.log")
    sys.stdout = open(log_file, "a")
    sys.stderr = open(log_file, "a")

def get_local_ipv4_address():
    """Get the local IPv4 address."""
    try:
        # Create a socket to get the local IP address
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))  # Google's public DNS server
            local_ip = s.getsockname()[0]
        return local_ip
    except Exception as e:
        if not IS_RUNNING_WITH_PYTHONW:
            print(f"Error getting local IP address: {e}")
        return "127.0.0.1"

class RemoteShutdownHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        """Override log method to prevent console output in pythonw."""
        if not IS_RUNNING_WITH_PYTHONW:
            super().log_message(format, *args)  # Only log to console if running with python.exe

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
        
        if not IS_RUNNING_WITH_PYTHONW:
            print(f"Request received: {self.path}")
        
        if "shutdown" in query_params and query_params["shutdown"][0] == "true" and \
           "token" in query_params and query_params["token"][0] == TOKEN:
            self.send_response_message(200, "Shutting down...")
            try:
                subprocess.run(["shutdown", "-s", "-f", "-t", "0"], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception as e:
                if not IS_RUNNING_WITH_PYTHONW:
                    print(f"Failed to execute shutdown command: {e}")
        else:
            self.send_response_message(400, "Invalid request.")

def run_server():
    """Run the HTTP server to listen for shutdown requests."""
    local_ip = get_local_ipv4_address()
    url = f"http://{local_ip}:{PORT_NUMBER}/"
    
    if not IS_RUNNING_WITH_PYTHONW:
        print(f"Listening for shutdown requests at {url}")

    with socketserver.TCPServer(("", PORT_NUMBER), RemoteShutdownHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            if not IS_RUNNING_WITH_PYTHONW:
                print("\nServer is shutting down...")
            httpd.shutdown()

def add_to_registry():
    """Add this script to Windows startup registry with pythonw.exe."""
    path_to_script = os.path.abspath(__file__)
    
    try:
        with reg.OpenKey(reg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, reg.KEY_ALL_ACCESS) as open_key:
            reg.SetValueEx(open_key, "RemoteShutdown", 0, reg.REG_SZ, f'"{Path(sys.executable).with_name("pythonw.exe")}" "{path_to_script}"')
    except Exception as e:
        if not IS_RUNNING_WITH_PYTHONW:
            print(f"Failed to add to registry: {e}")

if __name__ == "__main__":
    add_to_registry()
    run_server()
