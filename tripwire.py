import hashlib
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DECOY_FILE = ROOT / "decoys" / "network-backup.txt"
CHECK_EVERY_SECONDS = 1

def fingerprint():
    try:
        contents = DECOY_FILE.read_bytes()
    except FileNotFoundError:
        return None
    return hashlib.sha256(contents).hexdigest()

def main():
    DECOY_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not DECOY_FILE.exists():
        DECOY_FILE.write_text("Demo backup notes.\n", encoding="utf-8")

    old_fingerprint = fingerprint()
    print(f"Watching: {DECOY_FILE}")
    print("Change or delete the file.")