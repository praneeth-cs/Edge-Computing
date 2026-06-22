import numpy as np
import time
import random

# -----------------------------
# Component Classes
# -----------------------------

class Sensor:
    def generate_data(self):
        time.sleep(random.uniform(0.0005, 0.002))
        return np.random.rand()


class EdgeGateway:
    def preprocess(self, data):
        time.sleep(random.uniform(0.001, 0.003))
        return max(0, min(1, data))


class MLModel:
    def predict(self, data):
        confidence = random.uniform(0.4, 0.9)
        label = "HIGH" if data > 0.5 else "LOW"
        return label, confidence


class EdgeServer:
    def __init__(self):
        self.model = MLModel()

    def run_inference(self, data):
        time.sleep(random.uniform(0.005, 0.015))
        return self.model.predict(data)


class CloudServer:
    def run_inference(self, data):
        time.sleep(random.uniform(0.08, 0.15))
        confidence = random.uniform(0.7, 0.99)
        label = "HIGH" if data > 0.5 else "LOW"
        return label, confidence


# -----------------------------
# ASCII Architecture
# -----------------------------

def get_architecture():
    return """
+-----------+     +--------------+     +-------------+     +-------------+
|  Sensor   | --> | EdgeGateway  | --> | EdgeServer  | --> | CloudServer |
+-----------+     +--------------+     +-------------+     +-------------+
                        |                    |
                        |                    v
                        |              +-----------+
                        +------------> | ML Model  |
                                       +-----------+

Flow: Sensor → Gateway → Edge → (if confidence < 0.6) → Cloud
"""


# -----------------------------
# Simulation
# -----------------------------

def simulate(N=100):
    sensor = Sensor()
    gateway = EdgeGateway()
    edge = EdgeServer()
    cloud = CloudServer()

    lat_sensor = []
    lat_gateway = []
    lat_edge = []
    lat_cloud = []

    cloud_count = 0

    start_total = time.perf_counter()

    for _ in range(N):

        # Sensor
        t0 = time.perf_counter()
        data = sensor.generate_data()
        lat_sensor.append(time.perf_counter() - t0)

        # Gateway
        t0 = time.perf_counter()
        data = gateway.preprocess(data)
        lat_gateway.append(time.perf_counter() - t0)

        # Edge
        t0 = time.perf_counter()
        label, conf = edge.run_inference(data)
        lat_edge.append(time.perf_counter() - t0)

        # Conditional Cloud
        if conf < 0.6:
            cloud_count += 1
            t0 = time.perf_counter()
            label, conf = cloud.run_inference(data)
            lat_cloud.append(time.perf_counter() - t0)

    end_total = time.perf_counter()

    return {
        "sensor": lat_sensor,
        "gateway": lat_gateway,
        "edge": lat_edge,
        "cloud": lat_cloud,
        "cloud_count": cloud_count,
        "total_time": end_total - start_total,
        "N": N
    }


# -----------------------------
# Report Generation
# -----------------------------

def generate_report(results):
    def mean_ms(lst):
        return (sum(lst) / len(lst)) * 1000 if lst else 0

    report = "\n=== LATENCY REPORT ===\n"

    report += f"Sensor Avg Latency: {mean_ms(results['sensor']):.3f} ms\n"
    report += f"Gateway Avg Latency: {mean_ms(results['gateway']):.3f} ms\n"
    report += f"Edge Avg Latency: {mean_ms(results['edge']):.3f} ms\n"
    report += f"Cloud Avg Latency: {mean_ms(results['cloud']):.3f} ms\n"

    escalation = (results["cloud_count"] / results["N"]) * 100
    report += f"\nEscalated to Cloud: {escalation:.2f}%\n"

    throughput = results["N"] / results["total_time"]
    report += f"Throughput: {throughput:.2f} points/sec\n"

    return report


# -----------------------------
# Main
# -----------------------------

if __name__ == "__main__":

    architecture = get_architecture()
    results = simulate(100)
    report = generate_report(results)

    # Print to terminal
    print(architecture)
    print(report)

    # Write to file (overwrite mode)
    with open("latency_report.txt", "w") as f:
        f.write(architecture)
        f.write(report)