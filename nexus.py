#!/usr/bin/env python3

import hashlib
import json
import threading
import time
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

FOLDER = Path(__file__).resolve().parent
FILE = FOLDER / "decoys" / "nexus-test-file.txt"
LOG_FILE = FOLDER / "nexus-events.json"
CANARY_URL = "/internal/nexus-test-file.txt"
PORT = 8088
log_lock = threading.Lock()

def alert(alert_type, info):
    event = {
        "time": datetime.now().isoformat(timespec="seconds"),
        "type": alert_type,
        "info": info,
    }
    with log_lock:
        with LOG_FILE.open("a", encoding="utf-8") as log:
            log.write(json.dumps(event) + "\n")
    print("[NEXUS ALERT]", alert_type, "-", info, flush=True)

def file_hash():
    try:
        return hashlib.sha256(FILE.read_bytes()).hexdigest()
    except FileNotFoundError:
        return None

def watch_file():
    old_hash = file_hash()
    while True:
        time.sleep(1)
        new_hash = file_hash()
        if new_hash != old_hash:
            alert("File Change Detected", str(FILE.name))
            old_hash = new_hash

class CanaryServer(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.split("?")[0] == CANARY_URL:
            alert("Nexus URL Visited", self.client_address[0])
        self.send_response(404)
        self.end_headers()
        self.wfile.write(b"Not Found")
    def log_message(self, format, *args):
        # Suppress default request logs; relevant events are recorded by alert().
        pass

FILE.parent.mkdir(parents=True, exist_ok=True)

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
    
threading.Thread(target=watch_file, daemon=True).start()

server = HTTPServer(("127.0.0.1", PORT), CanaryServer)

print("Watching Nexus File:", FILE)
print(f"Watching Nexus URL: http://127.0.0.1:{PORT}{CANARY_URL}")

try:
    server.serve_forever()
except KeyboardInterrupt:
    print("\nNexus terminated.")
finally:
    server.server_close()