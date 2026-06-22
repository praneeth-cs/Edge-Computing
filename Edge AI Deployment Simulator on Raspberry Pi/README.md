# **Edge AI Deployment Simulator on Raspberry Pi**

## Overview

This project simulates an end-to-end Edge AI processing pipeline deployed under Raspberry Pi-like resource constraints. The system models the flow of sensor data through an edge computing architecture consisting of sensors, an edge gateway, an edge inference server, and a cloud inference service.

The simulation measures latency at each processing stage and evaluates the impact of cloud escalation when edge inference confidence falls below a predefined threshold.

---

## System Architecture

```text
Sensor
   │
   ▼
Edge Gateway
   │
   ▼
Edge Server (AI Inference)
   │
   ├── Confidence ≥ 0.60 → Edge Decision
   │
   └── Confidence < 0.60
            │
            ▼
      Cloud Server
```

---

## Features

- Synthetic sensor data generation
- Edge gateway preprocessing and filtering
- Edge AI inference simulation
- Cloud escalation based on confidence thresholds
- End-to-end latency measurement
- Throughput analysis
- ASCII architecture visualization
- Edge-to-cloud decision workflow

---

## Resource-Constrained Deployment Simulation

The system was designed and tested under Raspberry Pi-style constraints using a VirtualBox virtual machine configured as follows:

| Resource | Configuration |
|-----------|---------------|
| CPU Cores | 1 |
| RAM | 1 GB |
| CPU Execution Cap | 25–50% |
| Environment | Raspberry Pi Simulation |

These constraints emulate low-power edge computing environments where latency and resource utilization are critical factors.

---

## Workflow

1. Generate sensor readings
2. Preprocess data at the edge gateway
3. Run inference on the edge server
4. Evaluate prediction confidence
5. Escalate low-confidence predictions to the cloud
6. Measure latency across all stages
7. Generate performance metrics and reports

---

## Metrics Reported

- Mean sensor latency
- Mean gateway latency
- Mean edge inference latency
- Mean cloud inference latency
- Cloud escalation percentage
- Overall pipeline throughput (points/second)

---

## Installation

```bash
pip install numpy
```

---

## Run

```bash
python edge_architecture.py
```

---

## Output Files

```text
latency_report.txt
```

The report contains stage-level latency measurements, escalation statistics, and throughput metrics.

---

## Technologies Used

- Python
- NumPy
- Object-Oriented Programming
- Edge Computing Concepts
- AI Inference Simulation
- Performance Analysis
