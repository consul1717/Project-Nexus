# Project-Nexus
## Digital Tripwire and Network Canary
Project Nexus is a simple cybersecurity project I built using Python to detect activity through file monitoring and a fake network endpoint.
#### 
The goal of this project was to learn how intrusion detection works and how Python can be used to monitor activity, detect changes, and record security events.

## Features
### 1. File Integrity Monitor
- Monitors a decoy text file for changes
- Uses SHA-256 hashing to check file modified state
- Recursive check every second
- Creates an alert upon change detection
### 2. Network Canary
- Hosts fake webpage using Python's built-in HTTP server
- Detects decoy URL visits
- Records visitor's IP address
- Returns 404 response without exposing real file
### 3. Alert Logging
- Displays terminal alerts
- Saves events to nexus-events.json
- Records time, event type and revelant info

## Requirements
- Python 3
- Windows, macOS or Linux

## Requirements
1. Download or clone the Project-Nexus repository.
2. Open the project folder in a terminal.
3. Run the python script:
   `python nexus.py`

## File Monitoring
1. Open nexus-decoys/nexus-test-file.txt.
2. Modify the text.
3. Save the file.
4. Check the terminal.

Example output:

`[NEXUS ALERT] File Change Detected - nexus-test-file.txt`

## Network Monitoring
1. Open the following URL in your browser:
`http://127.0.0.1:8088/internal/nexus-test-file.txt`
2. Check the terminal.

Example output:

`[NEXUS ALERT] Nexus URL Visited - http://127.0.0.1`

These events will be saved to nexus-events.json.