import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import uuid
import os
import json

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import r2_score
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor

try:
    from xgboost import XGBRegressor
    xgb_available = True
except:
    xgb_available = False


# ---------------- CONFIG ---------------- #
MASTER_FILE = "master_sensor_data.csv"
STATS_FILE = "master_stats.json"

st.set_page_config(page_title="Sensor Simulator & ML Engine", layout="wide")
st.title("📊 Sensor Data Simulator & ML Engine")

# ---------------- UTILS ---------------- #
def smooth_random(prev, low, high, step=5):
    delta = np.random.randint(-step, step + 1)
    return int(np.clip(prev + delta, low, high))


def generate_sensor_data(start_dt):
    end_dt = start_dt + timedelta(hours=24)
    data = []

    sensors = {
        "S1": {"freq": timedelta(seconds=2), "range": (409, 818)},
        "S2": {"freq": timedelta(hours=4), "range": (246, 614)},
        "S3": {"freq": timedelta(seconds=5), "range": (0, 1023)},
    }

    for sensor, cfg in sensors.items():
        current = start_dt
        prev_val = np.random.randint(cfg["range"][0], cfg["range"][1])

        while current < end_dt:
            val = smooth_random(prev_val, *cfg["range"])
            data.append([
                current.date().isoformat(),
                current.time().strftime("%H:%M:%S"),
                sensor,
                val
            ])
            prev_val = val
            current += cfg["freq"]

    return pd.DataFrame(data, columns=["Date", "Time", "Sensor", "Value"]), end_dt


def load_master():
    if not os.path.exists(MASTER_FILE):
        pd.DataFrame(columns=["Date", "Time", "Sensor", "Value"]).to_csv(
            MASTER_FILE, index=False
        )
    return pd.read_csv(MASTER_FILE)


def load_stats():
    if not os.path.exists(STATS_FILE):
        stats = {"total_duplicates_removed": 0}
        with open(STATS_FILE, "w") as f:
            json.dump(stats, f)
        return stats
    with open(STATS_FILE, "r") as f:
        return json.load(f)


def update_stats(duplicates_removed):
    stats = load_stats()
    stats["total_duplicates_removed"] += duplicates_removed
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f)


def reset_master_and_stats():
    if os.path.exists(MASTER_FILE):
        os.remove(MASTER_FILE)
    if os.path.exists(STATS_FILE):
        os.remove(STATS_FILE)
    load_master()
    load_stats()


# ---------------- SECTION 1 ---------------- #
st.header("🧩 Section 1: Generate 24-Hour Sensor CSV")

col1, col2 = st.columns(2)
with col1:
    date_input = st.date_input("Select Start Date")
with col2:
    start_time = st.time_input("Select Start Time")

if st.button("Generate 24-Hour CSV"):
    start_dt = datetime.combine(date_input, start_time)
    df_generated, end_dt = generate_sensor_data(start_dt)

    st.info(
        f"Generating data from "
        f"{start_dt.strftime('%Y-%m-%d %H:%M:%S')} "
        f"to "
        f"{end_dt.strftime('%Y-%m-%d %H:%M:%S')}"
    )

    filename = (
        f"sensor_data_{start_dt.strftime('%Y-%m-%d_%H-%M-%S')}"
        f"_to_{end_dt.strftime('%Y-%m-%d_%H-%M-%S')}_{uuid.uuid4().hex[:6]}.csv"
    )

    df_generated.to_csv(filename, index=False)

    st.success(f"CSV generated: {filename}")
    st.dataframe(df_generated.head(20), use_container_width=True)

    with open(filename, "rb") as f:
        st.download_button(
            "⬇️ Download CSV",
            f,
            file_name=filename,
            mime="text/csv"
        )

st.divider()

# ---------------- SECTION 2 ---------------- #
st.header("🧩 Section 2: Master File Manager")

uploaded = st.file_uploader(
    "Upload generated CSV to append to Master File",
    type=["csv"]
)

if uploaded:
    new_df = pd.read_csv(uploaded)
    master_df = load_master()

    before = len(master_df)
    combined = pd.concat([master_df, new_df], ignore_index=True)

    before_dedup = len(combined)

    # ✅ Duplicate rule reverted to (Date, Time, Sensor)
    combined.drop_duplicates(
        subset=["Date", "Time", "Sensor"],
        keep="first",
        inplace=True
    )

    after = len(combined)
    added = after - before
    duplicates_removed = before_dedup - after

    combined.to_csv(MASTER_FILE, index=False)
    update_stats(duplicates_removed)

    st.success("Master file updated successfully")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Rows Added", added)
    with col2:
        st.metric("Duplicates Removed (This Upload)", duplicates_removed)

# ---- Master Statistics ---- #
st.subheader("📊 Master File Statistics")

master_df = load_master()
stats = load_stats()

col1, col2 = st.columns(2)
with col1:
    st.metric("Total Rows in Master File", len(master_df))
with col2:
    st.metric("Total Duplicates Removed (Overall)", stats["total_duplicates_removed"])

st.dataframe(master_df.tail(10), use_container_width=True)

# ---- Reset Button ---- #
st.warning("⚠️ Reset Master File")

if st.button("Reset Master File & Statistics"):
    reset_master_and_stats()
    st.success("Master file and metadata have been reset.")

st.divider()

# ---------------- SECTION 3 ---------------- #
st.header("🧩 Section 3: Machine Learning Engine")

if st.button("🚀 Initialize & Run Machine Learning Models"):
    df = load_master()

    if len(df) < 100:
        st.warning("Not enough data to train models (minimum 100 rows).")
    else:
        df["Date"] = pd.to_datetime(df["Date"])
        df["Hour"] = pd.to_datetime(df["Time"]).dt.hour
        df["Minute"] = pd.to_datetime(df["Time"]).dt.minute
        df["Second"] = pd.to_datetime(df["Time"]).dt.second
        df["Day"] = df["Date"].dt.day
        df["Weekday"] = df["Date"].dt.weekday

        le = LabelEncoder()
        df["SensorEncoded"] = le.fit_transform(df["Sensor"])

        X = df[["Hour", "Minute", "Second", "Day", "Weekday", "SensorEncoded"]]
        y = df["Value"]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        models = {
            "Linear Regression": LinearRegression(),
            "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42),
            "Gradient Boosting": GradientBoostingRegressor()
        }

        if xgb_available:
            models["XGBoost"] = XGBRegressor(
                objective="reg:squarederror",
                n_estimators=100,
                random_state=42
            )

        results = []

        with st.spinner("Training models (this may take a few minutes)..."):
            for name, model in models.items():
                model.fit(X_train, y_train)
                preds = model.predict(X_test)

                for sensor in ["S1", "S2", "S3"]:
                    mask = df.iloc[y_test.index]["Sensor"] == sensor
                    if mask.sum() > 0:
                        acc = r2_score(y_test[mask], preds[mask]) * 100
                        results.append({
                            "Model": name,
                            "Sensor": sensor,
                            "Accuracy (%)": round(acc, 2),
                            "Error (%)": round(100 - acc, 2)
                        })

        result_df = pd.DataFrame(results)

        best_model = (
            result_df.groupby("Model")["Accuracy (%)"]
            .mean()
            .idxmax()
        )

        st.success(f"🏆 Best Model: **{best_model}**")
        st.dataframe(result_df, use_container_width=True)
