# Project-Nexus
## Digital Tripwire and Network Canary
#### Project Nexus is a simple cybersecurity project I built using Python to detect activity through file monitoring and a fake network endpoint.
#### 
#### The goal of this project was to learn how intrusion detection works and how Python can be used to monitor activity, detect changes, and record security events.

## Features
### 1. File Integrity Monitor
###### - Monitors a decoy text file for changes
##### - Uses SHA-256 hashing to check file modified state
##### - Recursive check every second
##### - Creates an alert upon change detection
### 2. Network Canary
##### - Hosts fake webpage using Python's built-in HTTP server
##### - Detects decoy URL visits
##### - Records visitor's IP address
##### - Returns 404 response without exposing real file
### 3. Alert Logging
##### - Displays terminal alerts
##### - Saves events to nexus-events.json
##### - Records time, event type and revelant info


### Run: nexus.py
## MONITORED FILE AND URL
### http://127.0.0.1:8088/internal/nexus-test-file.txt
### decoys/nexus-test-file.txt
## JSON EVENT LOG
### nexus-events.json