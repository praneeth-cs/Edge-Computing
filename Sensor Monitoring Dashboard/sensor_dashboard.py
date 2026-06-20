import streamlit as st
import pandas as pd
import numpy as np
import time

# -------------------------------
# CONFIG
# -------------------------------
MAX_ADC = 1023
MIN_ADC = 0
INITIAL_AVG = 512
CONSECUTIVE_LIMIT = 1000
DEVIATION_THRESHOLD = 0.05

# -------------------------------
# SESSION INIT
# -------------------------------
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=[
        "time", "sensor", "threshold", "counter",
        "alarm", "deviation", "uploaded"
    ])
    st.session_state.avg = INITIAL_AVG
    st.session_state.counter = 0
    st.session_state.time = 0
    st.session_state.alarm = False

# -------------------------------
# SENSOR GENERATOR (REALISTIC BUT SIMPLE)
# -------------------------------
def generate_sensor(t):
    baseline = 512 + 40 * np.sin(t / 40)  # smooth pattern
    noise = np.random.randint(-15, 15)

    value = baseline + noise

    # occasional upward drift (trend)
    if np.random.rand() < 0.02:
        value += np.random.randint(50, 150)

    return int(max(MIN_ADC, min(MAX_ADC, value)))

# -------------------------------
# STEP FUNCTION
# -------------------------------
def step():
    t = st.session_state.time
    old_avg = st.session_state.avg

    sensor = generate_sensor(t)

    new_avg = (old_avg + sensor) / 2
    threshold = new_avg

    # consecutive logic
    if sensor > threshold:
        st.session_state.counter += 1
    else:
        st.session_state.counter = 0

    if st.session_state.counter >= CONSECUTIVE_LIMIT:
        st.session_state.alarm = True
        st.session_state.counter = 0

    deviation = abs(sensor - threshold) / threshold
    uploaded = deviation <= DEVIATION_THRESHOLD

    st.session_state.avg = new_avg

    new_row = {
        "time": t,
        "sensor": sensor,
        "threshold": threshold,
        "counter": st.session_state.counter,
        "alarm": st.session_state.alarm,
        "deviation": deviation,
        "uploaded": uploaded
    }

    st.session_state.data = pd.concat(
        [st.session_state.data, pd.DataFrame([new_row])],
        ignore_index=True
    )

    st.session_state.time += 1

# -------------------------------
# UI
# -------------------------------
st.title("📡 Sensor Monitoring Dashboard")

start = st.button("▶ Start Simulation")
reset = st.button("🔄 Reset")

if reset:
    st.session_state.data = st.session_state.data.iloc[0:0]
    st.session_state.avg = INITIAL_AVG
    st.session_state.counter = 0
    st.session_state.time = 0
    st.session_state.alarm = False

# placeholders
metrics = st.empty()
charts = st.empty()
table = st.empty()

# -------------------------------
# RUN LOOP (STABLE)
# -------------------------------
if start:
    for _ in range(10000):  # large loop = "continuous feel"
        step()

        df = st.session_state.data
        latest = df.iloc[-1]

        # METRICS
        with metrics.container():
            col1, col2, col3 = st.columns(3)
            col1.metric("Sensor", int(latest["sensor"]))
            col2.metric("Threshold", round(latest["threshold"], 2))
            col3.metric("Counter", int(latest["counter"]))

            col4, col5, col6 = st.columns(3)
            col4.metric("Alarm", "🚨 ON" if latest["alarm"] else "OFF")
            col5.metric("Deviation %", f"{latest['deviation']*100:.2f}%")
            col6.metric("Cloud Upload", "✅" if latest["uploaded"] else "❌")

        # CHARTS
        with charts.container():
            st.subheader("📈 Time vs Threshold")
            st.line_chart(df.set_index("time")[["threshold"]])

            st.subheader("📊 Sensor vs Threshold")
            st.line_chart(df.set_index("time")[["sensor", "threshold"]])

        # TABLE
        with table.container():
            st.subheader("📋 Recent Data")
            st.dataframe(df.tail(20), use_container_width=True)

        time.sleep(0.05)