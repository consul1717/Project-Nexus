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