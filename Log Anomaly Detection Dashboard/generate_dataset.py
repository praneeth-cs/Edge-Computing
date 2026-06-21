import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
import random

random.seed(42)
np.random.seed(42)

# ── Config ──────────────────────────────────────────────────────────────
START = datetime(2024, 1, 1, 0, 0, 0)
SERVICES = ["auth-service", "payment-service", "user-service", "api-gateway", "notification-service", "inventory-service", "order-service"]
USERS = [f"user_{i:03d}" for i in range(1, 51)] + ["admin_001", "admin_002", "bot_agent"]
NORMAL_IPS = [f"192.168.{r}.{c}" for r in range(1, 5) for c in range(1, 20)]
ATTACKER_IP = "10.0.0.99"
BOT_IP = "203.0.113.77"

GROUND_TRUTH = []
rows = []

def ts(base, delta_minutes):
    return base + timedelta(minutes=delta_minutes)

def log(timestamp, level, service, user, ip, response_ms, status_code, message=""):
    rows.append({
        "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        "level": level,
        "service": service,
        "user": user,
        "ip_address": ip,
        "response_time_ms": round(response_ms, 1),
        "status_code": status_code,
        "message": message or f"{level} from {service}"
    })

# ── Normal baseline traffic ──────────────────────────────────────────────
t = START
for day in range(7):
    base = START + timedelta(days=day)
    for hour in range(24):
        # lower traffic at night
        n = random.randint(5, 15) if 0 <= hour < 7 else random.randint(30, 80)
        for _ in range(n):
            minute = random.randint(0, 59)
            sec = random.randint(0, 59)
            t = base + timedelta(hours=hour, minutes=minute, seconds=sec)
            svc = random.choice(SERVICES)
            usr = random.choice(USERS[:-3])
            ip  = random.choice(NORMAL_IPS)
            rt  = max(20, np.random.normal(120, 40))
            sc  = random.choices([200, 201, 400, 404, 500], weights=[75,10,7,5,3])[0]
            lvl = "INFO" if sc < 400 else ("WARN" if sc < 500 else "ERROR")
            log(t, lvl, svc, usr, ip, rt, sc)

# ── Anomaly 1: Error Burst — day 1, ~02:15 ──────────────────────────────
ANOMALY_1_START = START + timedelta(days=1, hours=2, minutes=12)
for i in range(45):
    t = ANOMALY_1_START + timedelta(seconds=i * 4)
    log(t, "ERROR", "payment-service", random.choice(USERS[:20]), random.choice(NORMAL_IPS),
        random.uniform(800, 3000), 500, "Database connection pool exhausted")
GROUND_TRUTH.append({
    "anomaly_id": "A001",
    "type": "error_burst",
    "description": "45 errors in 3 minutes from payment-service",
    "start": ANOMALY_1_START.strftime("%Y-%m-%d %H:%M:%S"),
    "end": (ANOMALY_1_START + timedelta(minutes=3)).strftime("%Y-%m-%d %H:%M:%S"),
    "service": "payment-service",
    "severity": "critical"
})

# ── Anomaly 2: Brute-Force Login — day 2, 14:00 ─────────────────────────
ANOMALY_2_START = START + timedelta(days=2, hours=14, minutes=0)
for i in range(80):
    t = ANOMALY_2_START + timedelta(seconds=i * 6)
    log(t, "WARN", "auth-service", "unknown_attacker", ATTACKER_IP,
        random.uniform(50, 200), 401, "Authentication failed — invalid credentials")
GROUND_TRUTH.append({
    "anomaly_id": "A002",
    "type": "brute_force",
    "description": "80 failed logins from single IP in 8 minutes",
    "start": ANOMALY_2_START.strftime("%Y-%m-%d %H:%M:%S"),
    "end": (ANOMALY_2_START + timedelta(minutes=8)).strftime("%Y-%m-%d %H:%M:%S"),
    "ip_address": ATTACKER_IP,
    "service": "auth-service",
    "severity": "high"
})

# ── Anomaly 3: Traffic Spike from bot — day 3, 09:00 ────────────────────
ANOMALY_3_START = START + timedelta(days=3, hours=9, minutes=0)
for i in range(300):
    t = ANOMALY_3_START + timedelta(seconds=i * 2)
    svc = random.choice(["api-gateway", "user-service"])
    log(t, "INFO", svc, "bot_agent", BOT_IP,
        random.uniform(30, 90), 200, "Automated scraping request")
GROUND_TRUTH.append({
    "anomaly_id": "A003",
    "type": "traffic_spike",
    "description": "300 requests from single IP in 10 minutes (bot activity)",
    "start": ANOMALY_3_START.strftime("%Y-%m-%d %H:%M:%S"),
    "end": (ANOMALY_3_START + timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S"),
    "ip_address": BOT_IP,
    "severity": "medium"
})

# ── Anomaly 4: Service Degradation — day 4, 16:30 ───────────────────────
ANOMALY_4_START = START + timedelta(days=4, hours=16, minutes=30)
for i in range(60):
    t = ANOMALY_4_START + timedelta(minutes=i * 0.5)
    log(t, "WARN", "order-service", random.choice(USERS[:30]),
        random.choice(NORMAL_IPS), random.uniform(5000, 15000), 503,
        "Service response timeout — degraded performance")
GROUND_TRUTH.append({
    "anomaly_id": "A004",
    "type": "service_degradation",
    "description": "order-service avg response >5000ms for 30 minutes",
    "start": ANOMALY_4_START.strftime("%Y-%m-%d %H:%M:%S"),
    "end": (ANOMALY_4_START + timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M:%S"),
    "service": "order-service",
    "severity": "high"
})

# ── Anomaly 5: Off-hours Admin Activity — day 5, 03:17 ──────────────────
ANOMALY_5_START = START + timedelta(days=5, hours=3, minutes=17)
for i in range(25):
    t = ANOMALY_5_START + timedelta(minutes=i * 1.2)
    log(t, "INFO", "user-service", "admin_001", "10.0.0.55",
        random.uniform(100, 400), 200, "Admin bulk-export user records")
GROUND_TRUTH.append({
    "anomaly_id": "A005",
    "type": "off_hours_activity",
    "description": "Admin bulk data access at 03:17 — 25 export requests",
    "start": ANOMALY_5_START.strftime("%Y-%m-%d %H:%M:%S"),
    "end": (ANOMALY_5_START + timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M:%S"),
    "user": "admin_001",
    "service": "user-service",
    "severity": "medium"
})

# ── Anomaly 6: Critical System Failure — day 6, 22:00 ───────────────────
ANOMALY_6_START = START + timedelta(days=6, hours=22, minutes=0)
for i in range(90):
    t = ANOMALY_6_START + timedelta(seconds=i * 5)
    svc = random.choice(["api-gateway", "payment-service", "inventory-service"])
    log(t, "ERROR", svc, random.choice(USERS[:40]),
        random.choice(NORMAL_IPS), random.uniform(10000, 30000), 503,
        "CRITICAL: Cascading failure — upstream dependency unavailable")
GROUND_TRUTH.append({
    "anomaly_id": "A006",
    "type": "critical_failure",
    "description": "90 CRITICAL errors across 3 services in 7.5 minutes",
    "start": ANOMALY_6_START.strftime("%Y-%m-%d %H:%M:%S"),
    "end": (ANOMALY_6_START + timedelta(minutes=8)).strftime("%Y-%m-%d %H:%M:%S"),
    "services": ["api-gateway", "payment-service", "inventory-service"],
    "severity": "critical"
})

# ── Save files ────────────────────────────────────────────────────────────
df = pd.DataFrame(rows)
df = df.sort_values("timestamp").reset_index(drop=True)
df.to_csv("logs_dataset.csv", index=False)

gt_df = pd.DataFrame(GROUND_TRUTH)
gt_df.to_csv("ground_truth.csv", index=False)

with open("ground_truth.json", "w") as f:
    json.dump(GROUND_TRUTH, f, indent=2)

print(f"Dataset: {len(df)} rows | Ground truth: {len(GROUND_TRUTH)} anomalies")
print(df['level'].value_counts().to_string())
