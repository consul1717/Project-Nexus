#!/usr/bin/env python3

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

def record_event(event_type, **details):
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "event_type": event_type,
        **details,
    }
    with LOCK:
        with EVENT_FILE.open("a", encoding="utf-8") as file:
            file.write(json.dumps(event) + "\n")
    print(f"[ALERT] {event['timestamp']} {event_type}", flush=True)

def fingerprint():
    try:
        return hashlib.sha256(DECOY_FILE.read_bytes()).hexdigest()
    except FileNotFoundError:
        return None

def watch_file():
    old_fingerprint = fingerprint()
    while True:
        time.sleep(CHECK_EVERY_SECONDS)
        new_fingerprint = fingerprint()
        if new_fingerprint == old_fingerprint:
            continue

        if new_fingerprint is None:
            change = "deleted"
        elif old_fingerprint is None:
            change = "created"
        else:
            change = "modified"

        record_event("file_tripwire", file=DECOY_FILE.name, change=change)
        old_fingerprint = new_fingerprint

def main():
    DECOY_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not DECOY_FILE.exists():
        DECOY_FILE.write_text("Test.\n", encoding="utf-8")

if __name__ == "__main__":
    main()