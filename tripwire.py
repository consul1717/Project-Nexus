import hashlib
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DECOY_FILE = ROOT / "decoys" / "network-backup.txt"
CHECK_EVERY_SECONDS = 1