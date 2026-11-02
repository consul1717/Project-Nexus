#!/usr/bin/env python3

import argparse
import hashlib
import json
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
DECOY_FILE = ROOT / "decoys" / "network-backup.txt"
EVENT_FILE = ROOT / "events.json1"
CANARY_PATH = "/internal/network-backup.txt"
CHECK_EVERY_SECONDS = 1
LOCK = threading.Lock()

def record_event(event_type: str, **details):
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "event_type": event_type,
        **details,
    }
    with WRITE_LOCK: 
        with EVENT_FILE.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(event, ensure_ascii=True) + "\n")
    print(f"[ALERT] {event['timestamp']} {event_type}", flush=True)

def current_digest():
    try:
        return hashlib.sha256(DECOY_FILE.read_bytes()).hexdigest()
    except FileNotFoundError:
        return None

def watch_file():
    previous = current_digest()
    while True:
        time.sleep(POLL_SECONDS)
        digest = current_digest()
        if digest == previous:
            continue
        if previous is None:
            change = "created"
        elif digest is None:
            change = "deleted"
        else:
            change = "modified"
        record_event("file_tripwire", file=str(DECOY_FILE.relative_to(ROOT)), change=change)
        previous = digest

class CanaryHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Don't print raw, possibly untrusted request text in our terminal.
        pass

    def do_GET(self):
        route = urlsplit(self.path).path
        if route == CANARY_PATH:
            record_event(
                "digital_tripwire",
                source_ip=self.client_address[0],
                path=route,
            )
            message = "Error. Not found\n"
            status = 404
        else:
            message = "Systems operational\n"
            status = 200

        body = message.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

def main():
    DECOY_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not DECOY_FILE.exists():
        DECOY_FILE.write_text("Test.\n", encoding="utf-8")

    threading.Thread(target=watch_file, daemon=True).start()

    server = ThreadingHTTPServer(("127.0.0.1", 8088), CanaryHandler)
    print("Watching the decoy file, listening on http://127.0.0.1:8088",)
    print(f"Canary path: http://127.0.0.1:8088{CANARY_PATH}")
    print(f"Events go into: {EVENT_FILE}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping.")
    finally:
        server.server_close()

if __name__ == "__main__":
    main()