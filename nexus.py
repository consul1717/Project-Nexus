#!/usr/bin/env python3

import hashlib
import json
import threading
import time
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

# --- Configuration & Paths ---
# Locate script folder
FOLDER = Path(__file__).resolve().parent

# Define decoy file and JSON file
FILE = FOLDER / "nexus-decoys" / "nexus-test-file.txt"
LOG_FILE = FOLDER / "nexus-events.json"

# Decoy endpoint URL and port
CANARY_URL = "/internal/nexus-test-file.txt"
PORT = 8088

# Thread lock for logging to prevent multiple threads from writing to the log file simultaneously
log_lock = threading.Lock()

def alert(alert_type, info):
    # Logs events to JSON file + prints to terminal
    event = {
        "time": datetime.now().isoformat(timespec="seconds"),
        "type": alert_type,
        "info": info,
    }
    # Thread-safe writing to log file
    with log_lock:
        with LOG_FILE.open("a", encoding="utf-8") as log:
            log.write(json.dumps(event) + "\n")
    # Console alert parameters
    print("[NEXUS ALERT]", alert_type, "-", info, flush=True)

def file_hash():
    # Computes and returns SHA-256 hash of decoy file, returns None if file does not exist
    try:
        return hashlib.sha256(FILE.read_bytes()).hexdigest()
    except FileNotFoundError:
        return None

def watch_file():
    # Infinite loop to watch for changes in the decoy file, triggers alert if file is modified
    old_hash = file_hash()
    while True:
        time.sleep(1)
        new_hash = file_hash()
        if new_hash != old_hash:
            alert("File Change Detected", str(FILE.name))
            old_hash = new_hash

class CanaryServer(BaseHTTPRequestHandler):
    # Lightweight HTTP server designed to monitor access to the decoy URL
    def do_GET(self):
        # Extract the requested path and check if it matches the decoy URL, triggering an alert if accessed
        if self.path.split("?")[0] == CANARY_URL:
            # Trigger alert for decoy URL access
            alert("Nexus URL Visited", self.client_address[0])
        # Return a 404 Not Found response for all requests to the decoy URL
        self.send_response(404)
        self.end_headers()
        self.wfile.write(b"Error 404: Not Found")
    def log_message(self, format, *args):
        # Override to suppress default logging to console
        pass

# --- Initialisation & Setup ---

# Ensure the decoy file directory exists, creating it if necessary
FILE.parent.mkdir(parents=True, exist_ok=True)

# Generate the decoy file with placeholder content if it does not already exist
if not FILE.exists():
    FILE.write_text("# INTERNAL USE ONLY - PRODUCTION DATABASE CREDENTIALS\n"
                    "# Last Updated: October 2026\n"
                    "\n"
                    "[Production_DB]\n"
                    "Host = 10.0.4.25\n"
                    "Port = 5432\n"
                    "Username = db_admin_backup\n"
                    "Password = P@ssw0rd!_DropBox_Sync\n", 
                    encoding="utf-8")

# Start the file watcher in a separate daemon thread to monitor for changes in the decoy file
threading.Thread(target=watch_file, daemon=True).start()

# Start the HTTP server to listen for requests to the decoy URL, triggering alerts on access
server = HTTPServer(("127.0.0.1", PORT), CanaryServer)
print("Watching Nexus File:", FILE)
print(f"Watching Nexus URL: http://127.0.0.1:{PORT}{CANARY_URL}")

try:
    # Start the server and keep it running indefinitely, handling requests and monitoring for access to the decoy URL
    server.serve_forever()
except KeyboardInterrupt:
    print("\nNexus terminated.")
finally:
    # Cleanly close the server to free up resources and stop listening for requests
    server.server_close()