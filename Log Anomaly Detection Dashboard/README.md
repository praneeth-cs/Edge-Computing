# Log Anomaly Detection Dashboard

## Overview

Log Anomaly Detection Dashboard is a cybersecurity and DevOps analytics project that detects abnormal behavior in microservice logs using both rule-based detection and machine learning.

The project generates realistic log data, performs exploratory data analysis (EDA), applies anomaly detection techniques, evaluates detection performance, and visualizes results through an interactive Streamlit dashboard.

---

## Features

- Synthetic microservice log generation
- Exploratory Data Analysis (EDA)
- Rule-based anomaly detection
- Isolation Forest anomaly detection
- Real-time monitoring dashboard
- Alert generation and severity classification
- Detection performance evaluation
- Interactive visualizations and metrics

---

## Project Workflow

### Step 1: Dataset Generation
Generate realistic system logs containing normal activity and injected anomalies.

### Step 2: Exploratory Data Analysis
Analyze traffic patterns, response times, error frequencies, and service behavior.

### Step 3: Rule-Based Detection
Detect anomalies using predefined thresholds and sliding-window rules.

### Step 4: Machine Learning Detection
Apply Isolation Forest for unsupervised anomaly detection.

### Step 5: Evaluation
Compare detection methods using Precision, Recall, and F1 Score.

### Step 6: Dashboard Visualization
Monitor logs, alerts, anomalies, and system metrics through Streamlit.

---


## Installation

```bash
pip install -r requirements.txt
```

## Run Dashboard

```bash
streamlit run dashboard.py
```

## Technologies Used

- Python
- Streamlit
- Pandas
- NumPy
- Plotly
- Scikit-learn
- Matplotlib
- Seaborn
- ReportLab

## Future Improvements

- SHAP explainability
- Kafka integration
- Real-time log ingestion
- SIEM integration
- Cloud deployment

## License

Educational and research purposes.
