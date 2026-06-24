import random
from datetime import datetime, timedelta
import pandas as pd

NUM_READINGS = 100

records = []

local_processed = 0
uploaded = 0

warning_count = 0
critical_count = 0

start_time = datetime.now()


def calculate_health_score(hr, spo2, temp):
    score = 100

    # Heart Rate
    if hr < 60 or hr > 100:
        score -= 20

    # SpO2
    if spo2 < 95:
        score -= (95 - spo2) * 5

    # Temperature
    if temp > 37.5:
        score -= int((temp - 37.5) * 20)

    return max(0, min(100, int(score)))


def classify(score):
    if score >= 80:
        return "NORMAL"
    elif score >= 60:
        return "WARNING"
    return "CRITICAL"


for i in range(NUM_READINGS):

    timestamp = start_time + timedelta(seconds=i)

    heart_rate = random.randint(55, 110)
    spo2 = random.randint(92, 100)
    temperature = round(random.uniform(36.0, 39.0), 1)

    score = calculate_health_score(
        heart_rate,
        spo2,
        temperature
    )

    status = classify(score)

    if status == "NORMAL":
        local_processed += 1
    else:
        uploaded += 1

    if status == "WARNING":
        warning_count += 1

    if status == "CRITICAL":
        critical_count += 1

    records.append({
        "timestamp": timestamp,
        "heart_rate": heart_rate,
        "spo2": spo2,
        "temperature": temperature,
        "health_score": score,
        "status": status
    })

df = pd.DataFrame(records)

df.to_csv(
    "health_log.csv",
    index=False
)

avg_score = round(
    df["health_score"].mean(),
    2
)

bandwidth_saved = round(
    (local_processed / NUM_READINGS) * 100,
    2
)

report = f"""
Raspberry Pi Edge Health Monitoring Report
==========================================

Total Readings: {NUM_READINGS}

Average Health Score: {avg_score}

Warnings Detected: {warning_count}

Critical Alerts: {critical_count}

Processed Locally: {local_processed}

Uploaded To Cloud: {uploaded}

Bandwidth Saved: {bandwidth_saved}%
"""

with open(
    "health_report.txt",
    "w"
) as file:
    file.write(report)

print(report)

print("\\nGenerated:")
print("- health_log.csv")
print("- health_report.txt")