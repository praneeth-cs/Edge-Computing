# Edge Security Analytics on Raspberry Pi

## Overview

Edge Security Analytics on Raspberry Pi is a cybersecurity monitoring and attack detection system designed to operate under resource-constrained edge computing environments.

The project generates synthetic firewall and authentication logs, injects realistic attack scenarios, processes events in a streaming fashion, and detects malicious behavior using rule-based sliding window analysis.

The system identifies multiple attack categories, assigns severity and confidence scores, generates incident reports, and visualizes attack activity through timeline charts.

---

## Features

- Synthetic firewall and authentication log generation
- Streaming log processing
- Sliding window attack detection
- Brute-force attack detection
- Port scan detection
- DDoS detection
- Data exfiltration detection
- Severity classification
- Confidence scoring
- Incident report generation
- Attack timeline visualization

---

## System Workflow

### Step 1: Log Generation

Generate synthetic security logs containing:

- Source IP
- Destination IP
- Destination Port
- Action (ALLOW / DENY)
- Bytes Transferred
- Timestamp Information

---

### Step 2: Attack Injection

Inject realistic attack scenarios including:

- Brute Force Attempts
- Port Scans
- Distributed Denial of Service (DDoS)
- Data Exfiltration

---

### Step 3: Streaming Analysis

Process log events sequentially without loading the entire dataset into memory.

---

### Step 4: Sliding Window Detection

Apply rule-based detection algorithms to identify attack patterns within configurable time windows.

---

### Step 5: Threat Classification

Assign:

- Severity Levels
- Confidence Scores
- Incident Categories

---

### Step 6: Reporting and Visualization

Generate:

- Incident Reports
- Attack Timeline Charts
- Detection Summaries

---

## Resource-Constrained Deployment

The system was developed and tested under Raspberry Pi-style constraints using a VirtualBox virtual machine configured as follows:

| Resource | Configuration |
|-----------|---------------|
| CPU Cores | 1 |
| RAM | 1 GB |
| CPU Execution Cap | 25–50% |
| Environment | Raspberry Pi Simulation |

These constraints emulate low-power edge computing environments where efficient processing and memory management are critical.

---

## Detected Attack Types

### Brute Force Attack

- 50+ failed authentication attempts
- Single source IP
- 60-second detection window

### Port Scan

- 20+ sequential destination ports
- Single source IP
- 30-second detection window

### DDoS Attack

- 500+ requests per second
- 100+ source IP addresses
- Single target destination

### Data Exfiltration

- More than 500 MB transferred
- Single source IP
- 10-minute detection window

---

## Installation

```bash
pip install -r requirements.txt
```

---

## Run

```bash
python security_analyzer.py
```

---

## Output Files

```text
incident_report.txt
attack_timeline.png
```

The generated report contains detected attack incidents, confidence scores, severity levels, timestamps, and affected source IPs.

The timeline chart visualizes attack occurrences across the simulated environment.

---

## Technologies Used

- Python
- NumPy
- Pandas
- Matplotlib
- Sliding Window Algorithms
- Stream Processing
- Cybersecurity Analytics
- Edge Computing Concepts

---

## Future Improvements

- Real-time log ingestion
- MQTT-based event streaming
- Machine learning anomaly detection
- Dashboard-based monitoring
- Cloud synchronization
- Multi-node edge deployment simulation

---

## License

Educational and research purposes.
