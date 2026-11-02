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
DECOY_FILE = ROOT / "decoys" / "nexus-test-file.txt"
EVENT_FILE = ROOT / "events.json1"
CANARY_PATH = "/internal/nexus-test-file.txt"
POLL_SECONDS = 1.0
WRITE_LOCK = threading.Lock()

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

class Handler(BaseHTTPRequestHandler):
    server_version = "ProjectNexus/1.2"
    sys_version = ""

    def log_message(self, format, *args):
        # Disable logging of request paths/headers to terminal.
        pass

    def do_GET(self):
        self.handle_request(send_body=True)

    def do_HEAD(self):
        self.handle_request(send_body=False)

    def do_POST(self):
        self.handle_request(send_body=True)

    def handle_request(self, send_body):
        route = urlsplit(self.path).path
        if route == CANARY_PATH:
            record_event(
                "project_nexus",
                source_ip=self.client_address[0],
                method=self.command,
                path=route,
                user_agent=self.headers.get("User-Agent", "")[:160],
            )
            self.reply(404, "Not Found\n", send_body)
        elif route == "/health":
            self.reply(200, "OK\n", send_body)
        elif route == "/":
            self.reply(200, "Project Nexus is running.\n", send_body)
        else:
            self.reply(404, "Not Found\n", send_body)

    def reply(self, status, message, send_body):
        body = message.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if send_body:
            self.wfile.write(body)

def main():
    parser = argparse.ArgumentParser(description="Tripwire for Project Nexus.")
    parser.add_argument("--host", default="127.0.0.1", help="IP to listen on (default: localhost)")
    parser.add_argument("--port", type=int, default=8088, help="Port (default: 8088)")
    args = parser.parse_args()

    DECOY_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not DECOY_FILE.exists():
        DECOY_FILE.write_text(
            "***************************************************************************\n"
            "NOTICE: This is a restricted private network system.\n"
            "Authorized personnel only. All activities are monitored and recorded.\n"
            "Node: core-switch-01.infrastructure.local\n"
            "OS: Custom Embedded Linux v4.19.0-core\n"
            "***************************************************************************\n"
            "login: .\n",
            encoding="utf-8",
        )
    threading.Thread(target=watch_file, daemon=True).start()

    if args.host != "127.0.0.1" and args.port != "::1":
        print("WARNING: Use a trusted isolated lab/LAN only. Do not port forward.")
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"Project Nexus tripwire listening on {args.host}:{args.port}")
    print(f"Project Nexus URL: http://{args.host}:{args.port}{CANARY_PATH}")
    print(f"Watching {DECOY_FILE}")
    print(f"Events: {EVENT_FILE}")
    try:
        server.serve_forever(poll_interval=0.2)
    except KeyboardInterrupt:
        print("\nSession terminated.")
    finally:
        server.server_close()

if __name__ == "__main__":
    main()