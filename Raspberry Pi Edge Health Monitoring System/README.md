# Raspberry Pi Edge Health Monitoring System

## Overview

This project simulates a Raspberry Pi-based edge health monitoring platform that processes patient vital signs locally before deciding whether cloud escalation is required.

The system generates synthetic health sensor readings, calculates a health risk score, classifies patient status, and uploads only abnormal readings to the cloud, demonstrating edge-computing principles and bandwidth optimization.

---

## Features

- Heart Rate monitoring
- SpO2 monitoring
- Body Temperature monitoring
- Health Risk Score calculation (0–100)
- NORMAL / WARNING / CRITICAL classification
- Edge-to-cloud upload decisions
- CSV health log generation
- Health report generation
- Bandwidth savings statistics

---

## Workflow

Generate Sensor Readings
        ↓
Edge Health Analysis
        ↓
Health Risk Scoring
        ↓
NORMAL / WARNING / CRITICAL
        ↓
Cloud Upload Decision
        ↓
Bandwidth Optimization
        ↓
CSV Logging & Report Generation

---

## Output Files

```text
health_log.csv
health_report.txt
```

---

## Metrics

- Average Health Score
- Warning Count
- Critical Alert Count
- Readings Processed Locally
- Readings Uploaded to Cloud
- Estimated Bandwidth Saved

---

## Installation

```bash
pip install -r requirements.txt
```

---

## Run

```bash
python health_monitor.py
```

---

## Technologies Used

- Python
- NumPy
- Pandas
- Edge Computing
- Healthcare Analytics
- Sensor Data Simulation

---

## Future Improvements

- Real sensor integration
- MQTT-based data transmission
- Dashboard visualization
- Multi-patient monitoring
- Predictive health analytics

## License

Educational and research purposes.
