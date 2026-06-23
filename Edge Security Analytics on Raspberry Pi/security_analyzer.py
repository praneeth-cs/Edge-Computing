import random
import time
from collections import deque, defaultdict
import matplotlib.pyplot as plt

TOTAL_LOGS = 100000

# -----------------------------
# Synthetic Log Generator
# -----------------------------
def generate_logs():
    base_time = int(time.time())

    for i in range(TOTAL_LOGS):
        timestamp = base_time + i // 100

        log = {
            "timestamp": timestamp,
            "src_ip": f"192.168.1.{random.randint(1, 200)}",
            "dst_ip": f"10.0.0.{random.randint(1, 5)}",
            "dst_port": random.randint(20, 1024),
            "action": random.choice(["ALLOW", "DENY"]),
            "bytes_out": random.randint(100, 5000)
        }

        # ---- Inject Attacks ----

        # Brute Force
        if 1000 < i < 1060:
            log["src_ip"] = "192.168.1.250"
            log["action"] = "DENY"

        # Port Scan
        if 2000 < i < 2025:
            log["src_ip"] = "192.168.1.251"
            log["dst_port"] = 1000 + (i - 2000)

        # DDoS
        if 3000 < i < 3600:
            log["dst_ip"] = "10.0.0.99"
            log["src_ip"] = f"192.168.1.{i % 150}"

        # Data Exfiltration
        if 4000 < i < 4500:
            log["src_ip"] = "192.168.1.252"
            log["bytes_out"] = 2 * 1024 * 1024  # 2MB

        yield log


# -----------------------------
# Sliding Windows
# -----------------------------
brute_force = defaultdict(deque)
port_scan = defaultdict(deque)
ddos = defaultdict(lambda: defaultdict(set))
exfil = defaultdict(deque)

incidents = []
timeline = []

# ✅ Deduplication tracker
detected_flags = set()

# -----------------------------
# Detectors
# -----------------------------

def detect_bruteforce(log):
    if log["action"] != "DENY":
        return

    dq = brute_force[log["src_ip"]]
    dq.append(log["timestamp"])

    while dq and dq[0] < log["timestamp"] - 60:
        dq.popleft()

    key = ("brute", log["src_ip"])

    if len(dq) >= 50 and key not in detected_flags:
        detected_flags.add(key)

        confidence = min(100, (len(dq)/50)*100)
        incidents.append(("Brute Force", dq[0], dq[-1], log["src_ip"], confidence, "High"))
        timeline.append(log["timestamp"])
        dq.clear()


def detect_portscan(log):
    dq = port_scan[log["src_ip"]]
    dq.append((log["timestamp"], log["dst_port"]))

    while dq and dq[0][0] < log["timestamp"] - 30:
        dq.popleft()

    ports = sorted(set(p for _, p in dq))

    key = ("portscan", log["src_ip"])

    if len(ports) >= 20 and key not in detected_flags:
        detected_flags.add(key)

        confidence = min(100, (len(ports)/20)*100)
        incidents.append(("Port Scan", dq[0][0], dq[-1][0], log["src_ip"], confidence, "Medium"))
        timeline.append(log["timestamp"])
        dq.clear()


def detect_ddos(log):
    sec = log["timestamp"]
    ddos[sec][log["dst_ip"]].add(log["src_ip"])

    key = ("ddos", log["dst_ip"], sec)

    if len(ddos[sec][log["dst_ip"]]) >= 100 and key not in detected_flags:
        detected_flags.add(key)

        confidence = min(100, (len(ddos[sec][log["dst_ip"]])/100)*100)
        incidents.append(("DDoS", sec, sec, log["dst_ip"], confidence, "Critical"))
        timeline.append(sec)


def detect_exfiltration(log):
    dq = exfil[log["src_ip"]]
    dq.append((log["timestamp"], log["bytes_out"]))

    while dq and dq[0][0] < log["timestamp"] - 600:
        dq.popleft()

    total_bytes = sum(b for _, b in dq)

    key = ("exfil", log["src_ip"])

    if total_bytes > 500 * 1024 * 1024 and key not in detected_flags:
        detected_flags.add(key)

        confidence = min(100, (total_bytes/(500*1024*1024))*100)
        incidents.append(("Data Exfiltration", dq[0][0], dq[-1][0], log["src_ip"], confidence, "Critical"))
        timeline.append(log["timestamp"])
        dq.clear()


# -----------------------------
# Streaming Processing
# -----------------------------
for log in generate_logs():
    detect_bruteforce(log)
    detect_portscan(log)
    detect_ddos(log)
    detect_exfiltration(log)


# -----------------------------
# Write Incident Report
# -----------------------------
with open("incident_report.txt", "w") as f:
    f.write("Attack Type | Start | End | Source | Confidence | Severity\n")
    f.write("="*70 + "\n")

    for inc in incidents:
        f.write(f"{inc[0]} | {inc[1]} | {inc[2]} | {inc[3]} | {inc[4]:.2f}% | {inc[5]}\n")

print("incident_report.txt generated")

# -----------------------------
# Timeline Plot
# -----------------------------
if timeline:
    plt.figure()
    plt.scatter(timeline, range(len(timeline)))
    plt.xlabel("Time")
    plt.ylabel("Event Index")
    plt.title("Attack Timeline")
    plt.savefig("attack_timeline.png")
    print("attack_timeline.png generated")
else:
    print("No attacks detected")