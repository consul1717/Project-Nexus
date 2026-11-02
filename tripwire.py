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

def fingerprint():
    try:
        contents = DECOY_FILE.read_bytes()
    except FileNotFoundError:
        return None
    return hashlib.sha256(contents).hexdigest()

def main():
    DECOY_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not DECOY_FILE.exists():
        DECOY_FILE.write_text("Test.\n", encoding="utf-8")

    old_fingerprint = fingerprint()
    print(f"Tripwire deployed: {DECOY_FILE}")
    print("Change or delete the file.")

    try:
        while True:
            time.sleep(CHECK_EVERY_SECONDS)
            new_fingerprint = fingerprint()

            if new_fingerprint != old_fingerprint:
                if new_fingerprint is None:
                    change = "deleted"
                elif old_fingerprint is None:
                    change = "created"
                else:
                    change = "modified"

                time_of_alert = datetime.now().astimezone().isoformat(timespec="seconds")
                print(f"[ALERT] {time_of_alert} File {change}: {DECOY_FILE.name}")
                old_fingerprint = new_fingerprint
    except KeyboardInterrupt:
        print("\nExiting tripwire.")

if __name__ == "__main__":
    main()