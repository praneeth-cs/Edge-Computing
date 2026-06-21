"""
Log Anomaly Detection Dashboard
Streamlit app with live simulation, custom rules, and ML detection
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import LabelEncoder
import time
import random
import json
import warnings
warnings.filterwarnings("ignore")

# ─── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Log Anomaly Detection",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .main { background: #0d1117; }
    .block-container { padding: 1.5rem 2rem; max-width: 100%; }

    /* Header */
    .dash-header {
        background: linear-gradient(135deg, #1a1f2e 0%, #0f172a 100%);
        border: 1px solid #1e3a5f;
        border-radius: 12px;
        padding: 1.2rem 2rem;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    .dash-title { font-size: 1.6rem; font-weight: 700; color: #e2e8f0; margin: 0; }
    .dash-sub { font-size: 0.85rem; color: #64748b; margin: 0; }
    .live-badge {
        background: #16a34a22;
        border: 1px solid #16a34a;
        color: #4ade80;
        padding: 0.2rem 0.7rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        animation: pulse 2s infinite;
    }
    @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.6} }

    /* KPI Cards */
    .kpi-card {
        background: #1a1f2e;
        border: 1px solid #1e3a5f;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        position: relative;
        overflow: hidden;
    }
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
    }
    .kpi-critical::before { background: linear-gradient(90deg, #ef4444, #dc2626); }
    .kpi-high::before     { background: linear-gradient(90deg, #f97316, #ea580c); }
    .kpi-medium::before   { background: linear-gradient(90deg, #eab308, #ca8a04); }
    .kpi-info::before     { background: linear-gradient(90deg, #3b82f6, #2563eb); }

    .kpi-label  { font-size: 0.75rem; color: #94a3b8; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em; }
    .kpi-value  { font-size: 2rem; font-weight: 700; color: #e2e8f0; line-height: 1.2; }
    .kpi-delta  { font-size: 0.75rem; color: #64748b; margin-top: 0.2rem; }

    /* Alert cards */
    .alert-critical { background:#1c0a0a; border:1px solid #7f1d1d; border-left:4px solid #ef4444; border-radius:8px; padding:0.8rem 1rem; margin-bottom:0.5rem; }
    .alert-high     { background:#1c1308; border:1px solid #7c2d12; border-left:4px solid #f97316; border-radius:8px; padding:0.8rem 1rem; margin-bottom:0.5rem; }
    .alert-medium   { background:#1a1608; border:1px solid #713f12; border-left:4px solid #eab308; border-radius:8px; padding:0.8rem 1rem; margin-bottom:0.5rem; }

    .alert-type  { font-size:0.7rem; font-weight:700; letter-spacing:0.08em; text-transform:uppercase; }
    .alert-desc  { font-size:0.82rem; color:#cbd5e1; margin-top:0.2rem; }
    .alert-meta  { font-size:0.7rem; color:#64748b; margin-top:0.3rem; font-family:'JetBrains Mono',monospace; }

    .crit-txt { color:#fca5a5; }
    .high-txt { color:#fdba74; }
    .med-txt  { color:#fde047; }

    /* Log stream */
    .log-line {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        padding: 0.15rem 0;
        border-bottom: 1px solid #1e293b22;
    }
    .log-ERROR    { color: #fca5a5; }
    .log-CRITICAL { color: #f87171; background: #1c0a0a44; }
    .log-WARN     { color: #fde047; }
    .log-INFO     { color: #94a3b8; }
    .log-DEBUG    { color: #64748b; }

    /* Section headers */
    .section-header {
        font-size: 0.85rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.8rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .section-header::after {
        content: '';
        flex: 1;
        height: 1px;
        background: #1e293b;
    }

    /* Rule editor */
    .rule-card {
        background: #131923;
        border: 1px solid #1e3a5f44;
        border-radius: 8px;
        padding: 0.8rem 1rem;
        margin-bottom: 0.6rem;
    }

    /* Sidebar */
    .css-1d391kg, [data-testid="stSidebar"] {
        background: #0d1117 !important;
        border-right: 1px solid #1e293b !important;
    }

    /* Hide streamlit default elements */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }

    /* Status badges */
    .badge {
        display: inline-block;
        padding: 0.15rem 0.5rem;
        border-radius: 4px;
        font-size: 0.65rem;
        font-weight: 700;
        text-transform: uppercase;
    }
    .badge-critical { background:#7f1d1d; color:#fca5a5; }
    .badge-high     { background:#7c2d12; color:#fdba74; }
    .badge-medium   { background:#713f12; color:#fde047; }
    .badge-low      { background:#1e3a5f; color:#93c5fd; }

    /* Chart containers */
    .chart-container {
        background: #1a1f2e;
        border: 1px solid #1e3a5f;
        border-radius: 10px;
        padding: 1rem;
    }

    /* Plotly dark theme override */
    .js-plotly-plot .plotly { background: transparent !important; }
</style>
""", unsafe_allow_html=True)

# ─── Colour palette ──────────────────────────────────────────────────────────
PALETTE = {
    "INFO":     "#3b82f6",
    "WARN":     "#eab308",
    "ERROR":    "#ef4444",
    "CRITICAL": "#dc2626",
    "DEBUG":    "#64748b",
}
SEV_COLOR = {
    "CRITICAL": "#ef4444",
    "HIGH":     "#f97316",
    "MEDIUM":   "#eab308",
    "LOW":      "#3b82f6",
}
SERVICES = ["auth-service","payment-service","user-service","api-gateway",
            "notification-service","inventory-service","order-service"]
NORMAL_IPS = [f"192.168.{r}.{c}" for r in range(1,5) for c in range(1,20)]
ATTACKER_IP = "10.0.0.99"
BOT_IP = "203.0.113.77"
USERS = [f"user_{i:03d}" for i in range(1,51)] + ["admin_001","admin_002","bot_agent"]

# ─── Session state init ──────────────────────────────────────────────────────
def init_state():
    if "logs" not in st.session_state:
        try:
            df = pd.read_csv("logs_dataset.csv")
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            st.session_state.logs = df
        except:
            st.session_state.logs = pd.DataFrame(columns=[
                "timestamp","level","service","user","ip_address",
                "response_time_ms","status_code","message"
            ])
    if "anomalies" not in st.session_state:
        st.session_state.anomalies = []
    if "sim_running" not in st.session_state:
        st.session_state.sim_running = False
    if "rules" not in st.session_state:
        st.session_state.rules = [
            {"id":"R1","name":"Error Burst","enabled":True,
             "metric":"error_rate","threshold":20,"window_min":5,
             "severity":"HIGH","description":"Too many errors in window"},
            {"id":"R2","name":"Brute Force Login","enabled":True,
             "metric":"failed_auth","threshold":5,"window_min":1,
             "severity":"CRITICAL","description":"Repeated auth failures from same IP"},
            {"id":"R3","name":"Traffic Spike","enabled":True,
             "metric":"request_rate","threshold":100,"window_min":10,
             "severity":"MEDIUM","description":"Unusual request volume from single IP"},
            {"id":"R4","name":"Slow Response","enabled":True,
             "metric":"response_time","threshold":3000,"window_min":5,
             "severity":"HIGH","description":"Response time exceeds threshold"},
            {"id":"R5","name":"Off-Hours Admin","enabled":True,
             "metric":"off_hours_admin","threshold":5,"window_min":30,
             "severity":"MEDIUM","description":"Admin activity during 00:00–06:00"},
        ]
    if "ml_enabled" not in st.session_state:
        st.session_state.ml_enabled = True
    if "sim_tick" not in st.session_state:
        st.session_state.sim_tick = 0
    if "alert_history" not in st.session_state:
        st.session_state.alert_history = []

init_state()

# ─── Log generator (simulates real-time) ────────────────────────────────────
def generate_log_batch(n=5, inject_anomaly=None):
    rows = []
    now = datetime.now()
    for i in range(n):
        ts = now - timedelta(seconds=random.randint(0,10))
        svc = random.choice(SERVICES)
        usr = random.choice(USERS[:-3])
        ip  = random.choice(NORMAL_IPS)
        rt  = max(20, np.random.normal(120, 40))
        sc  = random.choices([200,201,400,404,500], weights=[75,10,7,5,3])[0]
        lvl = "INFO" if sc < 400 else ("WARN" if sc < 500 else "ERROR")
        rows.append(dict(timestamp=ts,level=lvl,service=svc,user=usr,
                         ip_address=ip,response_time_ms=round(rt,1),
                         status_code=sc,message=f"{lvl} from {svc}"))

    if inject_anomaly == "error_burst":
        for i in range(25):
            ts = now - timedelta(seconds=random.randint(0,60))
            rows.append(dict(timestamp=ts,level="ERROR",service="payment-service",
                             user=random.choice(USERS[:20]),ip_address=random.choice(NORMAL_IPS),
                             response_time_ms=round(random.uniform(800,3000),1),status_code=500,
                             message="DB connection pool exhausted"))
    elif inject_anomaly == "brute_force":
        for i in range(12):
            ts = now - timedelta(seconds=random.randint(0,30))
            rows.append(dict(timestamp=ts,level="WARN",service="auth-service",
                             user="unknown_attacker",ip_address=ATTACKER_IP,
                             response_time_ms=round(random.uniform(50,200),1),status_code=401,
                             message="Authentication failed"))
    elif inject_anomaly == "traffic_spike":
        for i in range(120):
            ts = now - timedelta(seconds=random.randint(0,300))
            rows.append(dict(timestamp=ts,level="INFO",service="api-gateway",
                             user="bot_agent",ip_address=BOT_IP,
                             response_time_ms=round(random.uniform(30,90),1),status_code=200,
                             message="Automated scraping request"))
    elif inject_anomaly == "slow_response":
        for i in range(30):
            ts = now - timedelta(seconds=random.randint(0,120))
            rows.append(dict(timestamp=ts,level="WARN",service="order-service",
                             user=random.choice(USERS[:30]),ip_address=random.choice(NORMAL_IPS),
                             response_time_ms=round(random.uniform(5000,15000),1),status_code=503,
                             message="Service response timeout"))
    return pd.DataFrame(rows)

# ─── Rule engine ─────────────────────────────────────────────────────────────
def run_rules(df, rules):
    alerts = []
    if len(df) == 0:
        return alerts
    now = df["timestamp"].max()

    for rule in rules:
        if not rule["enabled"]:
            continue
        win = timedelta(minutes=rule["window_min"])
        window_df = df[df["timestamp"] >= now - win]

        if rule["metric"] == "error_rate":
            errors = window_df[window_df["level"] == "ERROR"]
            if len(errors) >= rule["threshold"]:
                alerts.append({
                    "time": now.strftime("%H:%M:%S"),
                    "rule": rule["name"],
                    "severity": rule["severity"],
                    "details": f"{len(errors)} errors in {rule['window_min']}min window",
                    "service": errors["service"].mode()[0] if len(errors) else "—",
                    "ip": "multiple",
                })

        elif rule["metric"] == "failed_auth":
            failed = window_df[(window_df["service"]=="auth-service")&(window_df["status_code"]==401)]
            by_ip = failed.groupby("ip_address").size()
            for ip, cnt in by_ip.items():
                if cnt >= rule["threshold"]:
                    alerts.append({
                        "time": now.strftime("%H:%M:%S"),
                        "rule": rule["name"],
                        "severity": rule["severity"],
                        "details": f"{cnt} failed auth from {ip} in {rule['window_min']}min",
                        "service": "auth-service",
                        "ip": ip,
                    })

        elif rule["metric"] == "request_rate":
            by_ip = window_df.groupby("ip_address").size()
            for ip, cnt in by_ip.items():
                if cnt >= rule["threshold"]:
                    alerts.append({
                        "time": now.strftime("%H:%M:%S"),
                        "rule": rule["name"],
                        "severity": rule["severity"],
                        "details": f"{cnt} requests from {ip} in {rule['window_min']}min",
                        "service": window_df[window_df["ip_address"]==ip]["service"].mode()[0],
                        "ip": ip,
                    })

        elif rule["metric"] == "response_time":
            slow = window_df[window_df["response_time_ms"] > rule["threshold"]]
            by_svc = slow.groupby("service").size()
            for svc, cnt in by_svc.items():
                if cnt >= 5:
                    alerts.append({
                        "time": now.strftime("%H:%M:%S"),
                        "rule": rule["name"],
                        "severity": rule["severity"],
                        "details": f"{cnt} responses >{rule['threshold']}ms from {svc}",
                        "service": svc,
                        "ip": "multiple",
                    })

        elif rule["metric"] == "off_hours_admin":
            hour = now.hour
            if 0 <= hour < 6:
                admin = window_df[window_df["user"].str.startswith("admin", na=False)]
                if len(admin) >= rule["threshold"]:
                    alerts.append({
                        "time": now.strftime("%H:%M:%S"),
                        "rule": rule["name"],
                        "severity": rule["severity"],
                        "details": f"Admin active at {hour:02d}:xx — {len(admin)} requests",
                        "service": admin["service"].iloc[0] if len(admin) else "—",
                        "ip": admin["ip_address"].iloc[0] if len(admin) else "—",
                    })
    return alerts

# ─── ML detection ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=30)
def run_ml(df_json):
    df = pd.read_json(df_json, convert_dates=["timestamp"])
    if len(df) < 50:
        return pd.DataFrame()
    le = LabelEncoder()
    df["level_enc"]   = le.fit_transform(df["level"])
    df["service_enc"] = le.fit_transform(df["service"].fillna("unknown"))
    df["user_enc"]    = le.fit_transform(df["user"].fillna("unknown"))
    df["is_error"]    = (df["status_code"] >= 400).astype(int)
    df["is_5xx"]      = (df["status_code"] >= 500).astype(int)
    df["hour"]        = pd.to_datetime(df["timestamp"]).dt.hour
    df["is_offhour"]  = ((df["hour"] < 6) | (df["hour"] > 22)).astype(int)
    df["rt_log"]      = np.log1p(df["response_time_ms"])
    FEATURES = ["hour","level_enc","service_enc","user_enc","response_time_ms",
                "rt_log","status_code","is_error","is_5xx","is_offhour"]
    X = df[FEATURES].fillna(0)
    clf = IsolationForest(contamination=0.05, n_estimators=100, random_state=42)
    df["prediction"]    = clf.fit_predict(X)
    df["anomaly_score"] = clf.score_samples(X)
    df["is_anomaly"]    = df["prediction"] == -1
    return df[df["is_anomaly"]][["timestamp","level","service","user","ip_address",
                                  "response_time_ms","status_code","anomaly_score"]].head(50)

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🛡️ AnomalyGuard")
    st.markdown("---")

    st.markdown("#### ⚡ Live Simulation")
    sim_col1, sim_col2 = st.columns(2)
    with sim_col1:
        if st.button("▶ Start" if not st.session_state.sim_running else "⏸ Pause",
                     use_container_width=True):
            st.session_state.sim_running = not st.session_state.sim_running
    with sim_col2:
        if st.button("↺ Reset", use_container_width=True):
            st.session_state.sim_running = False
            st.session_state.sim_tick = 0
            st.session_state.anomalies = []
            st.session_state.alert_history = []
            try:
                df = pd.read_csv("logs_dataset.csv")
                df["timestamp"] = pd.to_datetime(df["timestamp"])
                st.session_state.logs = df
            except:
                st.session_state.logs = pd.DataFrame(columns=["timestamp","level","service","user","ip_address","response_time_ms","status_code","message"])
            st.rerun()

    st.markdown("#### 💉 Inject Anomaly")
    inj_map = {
        "🔴 Error Burst": "error_burst",
        "🟣 Brute Force": "brute_force",
        "🟡 Traffic Spike": "traffic_spike",
        "🟠 Slow Response": "slow_response",
    }
    for label, key in inj_map.items():
        if st.button(label, use_container_width=True):
            new_logs = generate_log_batch(5, inject_anomaly=key)
            new_logs["timestamp"] = pd.Timestamp.now()
            st.session_state.logs = pd.concat([st.session_state.logs, new_logs], ignore_index=True)
            alerts = run_rules(st.session_state.logs.tail(500), st.session_state.rules)
            st.session_state.alert_history = (alerts + st.session_state.alert_history)[:50]
            st.rerun()

    st.markdown("---")
    st.markdown("#### ⚙️ Settings")
    st.session_state.ml_enabled = st.toggle("ML Detection (Isolation Forest)", value=st.session_state.ml_enabled)
    sim_speed = st.slider("Sim speed (logs/tick)", 3, 20, 8)
    time_window = st.slider("Dashboard window (min)", 5, 60, 30)

    st.markdown("---")
    st.markdown("#### 🔍 Filters")
    svc_filter = st.multiselect("Services", SERVICES, default=SERVICES)
    lvl_filter = st.multiselect("Log Levels", ["INFO","WARN","ERROR","CRITICAL"], default=["INFO","WARN","ERROR","CRITICAL"])

# ─── Simulate tick ────────────────────────────────────────────────────────────
if st.session_state.sim_running:
    new_logs = generate_log_batch(sim_speed)
    st.session_state.logs = pd.concat([st.session_state.logs, new_logs], ignore_index=True)
    # Keep last 10k rows
    if len(st.session_state.logs) > 10000:
        st.session_state.logs = st.session_state.logs.tail(10000).reset_index(drop=True)
    st.session_state.sim_tick += 1
    # Run rules
    alerts = run_rules(st.session_state.logs.tail(500), st.session_state.rules)
    if alerts:
        st.session_state.alert_history = (alerts + st.session_state.alert_history)[:50]

# ─── Filter data ─────────────────────────────────────────────────────────────
df = st.session_state.logs.copy()
df = df[df["service"].isin(svc_filter)]
df = df[df["level"].isin(lvl_filter)]
if len(df) > 0:
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    cutoff = df["timestamp"].max() - timedelta(minutes=time_window)
    df_win = df[df["timestamp"] >= cutoff].copy()
else:
    df_win = df.copy()

# ─── Header ───────────────────────────────────────────────────────────────────
status = "🟢 LIVE" if st.session_state.sim_running else "⚪ PAUSED"
st.markdown(f"""
<div class="dash-header">
    <div>
        <p class="dash-title">🛡️ AnomalyGuard Dashboard</p>
        <p class="dash-sub">TechCorp Inc — Microservice Log Anomaly Detection</p>
    </div>
    <div style="margin-left:auto; display:flex; align-items:center; gap:1rem;">
        <span class="live-badge">{status}</span>
        <span style="color:#64748b; font-size:0.8rem;">Tick #{st.session_state.sim_tick} &nbsp;|&nbsp; {len(st.session_state.logs):,} total logs</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── KPI Row ──────────────────────────────────────────────────────────────────
total = len(df_win)
errors = len(df_win[df_win["level"]=="ERROR"]) if total else 0
warnings = len(df_win[df_win["level"]=="WARN"]) if total else 0
alerts_count = len(st.session_state.alert_history)
avg_rt = df_win["response_time_ms"].mean() if total else 0
critical_count = sum(1 for a in st.session_state.alert_history if a["severity"] == "CRITICAL")

k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    st.markdown(f"""<div class="kpi-card kpi-info">
        <div class="kpi-label">📊 Total Logs</div>
        <div class="kpi-value">{total:,}</div>
        <div class="kpi-delta">Last {time_window} minutes</div>
    </div>""", unsafe_allow_html=True)
with k2:
    st.markdown(f"""<div class="kpi-card kpi-critical">
        <div class="kpi-label">🔴 Errors</div>
        <div class="kpi-value" style="color:#ef4444">{errors:,}</div>
        <div class="kpi-delta">{(errors/max(total,1)*100):.1f}% of logs</div>
    </div>""", unsafe_allow_html=True)
with k3:
    st.markdown(f"""<div class="kpi-card kpi-high">
        <div class="kpi-label">⚠️ Warnings</div>
        <div class="kpi-value" style="color:#f97316">{warnings:,}</div>
        <div class="kpi-delta">{(warnings/max(total,1)*100):.1f}% of logs</div>
    </div>""", unsafe_allow_html=True)
with k4:
    st.markdown(f"""<div class="kpi-card kpi-medium">
        <div class="kpi-label">🚨 Active Alerts</div>
        <div class="kpi-value" style="color:#eab308">{alerts_count}</div>
        <div class="kpi-delta">{critical_count} critical</div>
    </div>""", unsafe_allow_html=True)
with k5:
    rt_color = "#ef4444" if avg_rt > 2000 else ("#eab308" if avg_rt > 500 else "#4ade80")
    st.markdown(f"""<div class="kpi-card kpi-info">
        <div class="kpi-label">⏱️ Avg Response</div>
        <div class="kpi-value" style="color:{rt_color}">{avg_rt:.0f}ms</div>
        <div class="kpi-delta">across all services</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Main content: 3-column layout ───────────────────────────────────────────
left, mid, right = st.columns([2.2, 2.5, 1.8])

# ── LEFT: Charts ──────────────────────────────────────────────────────────────
with left:
    st.markdown('<div class="section-header">📈 Traffic & Anomaly Timeline</div>', unsafe_allow_html=True)
    if len(df_win) > 0:
        df_ts = df_win.set_index("timestamp").resample("1min")["level"].count().reset_index()
        df_ts.columns = ["time","count"]
        err_ts = df_win[df_win["level"]=="ERROR"].set_index("timestamp").resample("1min")["level"].count().reset_index()
        err_ts.columns = ["time","errors"]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_ts["time"], y=df_ts["count"],
            fill="tozeroy", name="Total",
            line=dict(color="#3b82f6", width=2),
            fillcolor="rgba(59,130,246,0.1)"
        ))
        fig.add_trace(go.Scatter(
            x=err_ts["time"], y=err_ts["errors"],
            fill="tozeroy", name="Errors",
            line=dict(color="#ef4444", width=2),
            fillcolor="rgba(239,68,68,0.2)"
        ))
        # Mark alert times
        for a in st.session_state.alert_history[:5]:
            try:
                at = pd.Timestamp(a["time"])
                fig.add_vline(x=at, line_color="#fde047", line_width=1, line_dash="dash", opacity=0.4)
            except:
                pass
        fig.update_layout(
            paper_bgcolor="#1a1f2e", plot_bgcolor="#1a1f2e",
            font=dict(color="#94a3b8", size=11),
            margin=dict(l=10,r=10,t=10,b=10),
            legend=dict(bgcolor="#1a1f2e", bordercolor="#1e3a5f", x=0, y=1),
            xaxis=dict(showgrid=False, color="#64748b"),
            yaxis=dict(showgrid=True, gridcolor="#1e293b", color="#64748b"),
            height=200,
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
    else:
        st.info("No data in selected window")

    st.markdown('<div class="section-header">🔵 Log Level Distribution</div>', unsafe_allow_html=True)
    if len(df_win) > 0:
        lvl_counts = df_win["level"].value_counts().reset_index()
        lvl_counts.columns = ["level","count"]
        fig2 = go.Figure(go.Bar(
            x=lvl_counts["level"],
            y=lvl_counts["count"],
            marker_color=[PALETTE.get(l,"#888") for l in lvl_counts["level"]],
            text=lvl_counts["count"],
            textposition="outside",
            textfont=dict(color="#e2e8f0", size=11)
        ))
        fig2.update_layout(
            paper_bgcolor="#1a1f2e", plot_bgcolor="#1a1f2e",
            font=dict(color="#94a3b8"),
            margin=dict(l=10,r=10,t=10,b=10),
            xaxis=dict(showgrid=False, color="#64748b"),
            yaxis=dict(showgrid=True, gridcolor="#1e293b", color="#64748b"),
            height=175,
        )
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar":False})

    st.markdown('<div class="section-header">⚡ Response Time by Service</div>', unsafe_allow_html=True)
    if len(df_win) > 0:
        rt_svc = df_win.groupby("service")["response_time_ms"].mean().sort_values(ascending=True).reset_index()
        colors = ["#ef4444" if v > 2000 else "#eab308" if v > 500 else "#4ade80" for v in rt_svc["response_time_ms"]]
        fig3 = go.Figure(go.Bar(
            x=rt_svc["response_time_ms"],
            y=rt_svc["service"],
            orientation="h",
            marker_color=colors,
            text=[f"{v:.0f}ms" for v in rt_svc["response_time_ms"]],
            textposition="outside",
            textfont=dict(color="#e2e8f0", size=10)
        ))
        fig3.update_layout(
            paper_bgcolor="#1a1f2e", plot_bgcolor="#1a1f2e",
            font=dict(color="#94a3b8"),
            margin=dict(l=10,r=10,t=10,b=10),
            xaxis=dict(showgrid=True, gridcolor="#1e293b", color="#64748b"),
            yaxis=dict(showgrid=False, color="#94a3b8", tickfont=dict(size=10)),
            height=220,
        )
        st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar":False})

# ── MID: Alerts + Custom Rules ────────────────────────────────────────────────
with mid:
    st.markdown('<div class="section-header">🚨 Active Alerts</div>', unsafe_allow_html=True)

    if st.session_state.alert_history:
        for a in st.session_state.alert_history[:8]:
            sev = a["severity"]
            cls = {"CRITICAL":"alert-critical crit-txt","HIGH":"alert-high high-txt","MEDIUM":"alert-medium med-txt"}.get(sev,"alert-medium med-txt")
            tcls = {"CRITICAL":"crit-txt","HIGH":"high-txt","MEDIUM":"med-txt"}.get(sev,"med-txt")
            icons = {"CRITICAL":"🔴","HIGH":"🟠","MEDIUM":"🟡","LOW":"🔵"}
            st.markdown(f"""
            <div class="{cls.split()[0]}">
                <div class="alert-type {tcls}">{icons.get(sev,'⚪')} {sev} — {a['rule']}</div>
                <div class="alert-desc">{a['details']}</div>
                <div class="alert-meta">⏱ {a['time']} &nbsp;|&nbsp; 🔧 {a['service']} &nbsp;|&nbsp; 🌐 {a['ip']}</div>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""<div style="background:#131923;border:1px dashed #1e3a5f;border-radius:8px;padding:2rem;text-align:center;color:#475569;">
            <div style="font-size:2rem;margin-bottom:0.5rem">✅</div>
            <div>No active alerts — system normal</div>
            <div style="font-size:0.75rem;margin-top:0.3rem">Inject an anomaly or start simulation to see alerts</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">⚙️ Custom Detection Rules</div>', unsafe_allow_html=True)

    # Rule editor
    for idx, rule in enumerate(st.session_state.rules):
        with st.expander(f"{'✅' if rule['enabled'] else '⬜'} {rule['name']} — {rule['severity']}", expanded=False):
            c1, c2, c3 = st.columns([1,1,1])
            with c1:
                rule["enabled"] = st.toggle("Enabled", value=rule["enabled"], key=f"en_{rule['id']}")
            with c2:
                rule["threshold"] = st.number_input("Threshold", value=rule["threshold"], min_value=1, key=f"th_{rule['id']}")
            with c3:
                rule["window_min"] = st.number_input("Window (min)", value=rule["window_min"], min_value=1, key=f"win_{rule['id']}")
            rule["severity"] = st.selectbox("Severity", ["LOW","MEDIUM","HIGH","CRITICAL"],
                                             index=["LOW","MEDIUM","HIGH","CRITICAL"].index(rule["severity"]),
                                             key=f"sev_{rule['id']}")

    st.markdown("<br>", unsafe_allow_html=True)

    # Add custom rule
    with st.expander("➕ Add Custom Rule"):
        nr_name = st.text_input("Rule Name", placeholder="e.g. DDoS Guard")
        nr_metric = st.selectbox("Metric", ["error_rate","failed_auth","request_rate","response_time","off_hours_admin"])
        nc1, nc2 = st.columns(2)
        with nc1:
            nr_threshold = st.number_input("Threshold", value=10, min_value=1)
        with nc2:
            nr_window = st.number_input("Window (min)", value=5, min_value=1)
        nr_severity = st.selectbox("Severity", ["LOW","MEDIUM","HIGH","CRITICAL"], index=2)
        if st.button("Add Rule", use_container_width=True):
            if nr_name:
                new_id = f"R{len(st.session_state.rules)+1}"
                st.session_state.rules.append({
                    "id": new_id, "name": nr_name, "enabled": True,
                    "metric": nr_metric, "threshold": nr_threshold,
                    "window_min": nr_window, "severity": nr_severity,
                    "description": f"Custom rule: {nr_name}"
                })
                st.success(f"Rule '{nr_name}' added!")
                st.rerun()

# ── RIGHT: Live Log Stream + ML ───────────────────────────────────────────────
with right:
    st.markdown('<div class="section-header">📟 Live Log Stream</div>', unsafe_allow_html=True)

    if len(df_win) > 0:
        recent = df_win.sort_values("timestamp", ascending=False).head(40)
        log_html = '<div style="background:#0d1117;border:1px solid #1e293b;border-radius:8px;padding:0.8rem;height:280px;overflow-y:auto;font-family:JetBrains Mono,monospace;font-size:0.68rem;">'
        for _, row in recent.iterrows():
            lvl = row["level"]
            color = {"INFO":"#64748b","WARN":"#fde047","ERROR":"#fca5a5","CRITICAL":"#f87171","DEBUG":"#475569"}.get(lvl,"#64748b")
            ts_str = str(row["timestamp"])[-8:][:8]
            log_html += f'<div style="color:{color};padding:1px 0;border-bottom:1px solid #0f172a;">'
            log_html += f'{ts_str} <span style="color:#475569">[{row["service"][:10]:<10}]</span> <b>{lvl}</b> {row["status_code"]} {row["response_time_ms"]:.0f}ms'
            log_html += f'</div>'
        log_html += '</div>'
        st.markdown(log_html, unsafe_allow_html=True)
    else:
        st.markdown('<div style="background:#0d1117;border:1px dashed #1e293b;border-radius:8px;padding:2rem;text-align:center;color:#475569;height:280px;display:flex;align-items:center;justify-content:center;">No logs in window</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">🤖 ML Anomaly Scores</div>', unsafe_allow_html=True)

    if st.session_state.ml_enabled and len(df_win) >= 50:
        try:
            ml_df = run_ml(df_win.tail(1000).to_json())
            if len(ml_df) > 0:
                st.markdown(f"<div style='color:#94a3b8;font-size:0.75rem;margin-bottom:0.5rem'>🤖 {len(ml_df)} anomalies flagged by Isolation Forest</div>", unsafe_allow_html=True)
                ml_top = ml_df.head(8)
                for _, row in ml_top.iterrows():
                    score_pct = max(0, min(100, int((1 + row["anomaly_score"]) * 50)))
                    score_color = "#ef4444" if score_pct < 30 else "#eab308" if score_pct < 60 else "#4ade80"
                    ts_str = str(row["timestamp"])[-8:][:8]
                    st.markdown(f"""
                    <div style="background:#131923;border:1px solid #1e3a5f22;border-radius:6px;padding:0.5rem 0.7rem;margin-bottom:0.35rem;">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <span style="color:#94a3b8;font-size:0.72rem;font-family:JetBrains Mono">{row['service'][:18]}</span>
                            <span style="color:{score_color};font-size:0.7rem;font-weight:700">Score {score_pct}%</span>
                        </div>
                        <div style="color:#64748b;font-size:0.65rem;font-family:JetBrains Mono;margin-top:0.2rem">
                            {ts_str} &nbsp;·&nbsp; {row['status_code']} &nbsp;·&nbsp; {row['response_time_ms']:.0f}ms
                        </div>
                        <div style="background:#0d1117;height:3px;border-radius:2px;margin-top:0.3rem;">
                            <div style="background:{score_color};height:3px;border-radius:2px;width:{100-score_pct}%;"></div>
                        </div>
                    </div>""", unsafe_allow_html=True)
            else:
                st.markdown('<div style="color:#4ade80;font-size:0.8rem;text-align:center;padding:1rem">✅ No ML anomalies detected</div>', unsafe_allow_html=True)
        except Exception as e:
            st.markdown(f'<div style="color:#64748b;font-size:0.75rem">ML processing... ({str(e)[:40]})</div>', unsafe_allow_html=True)
    elif not st.session_state.ml_enabled:
        st.markdown('<div style="color:#475569;font-size:0.8rem;text-align:center;padding:1rem">ML detection disabled</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="color:#475569;font-size:0.8rem;text-align:center;padding:1rem">Need ≥50 logs for ML analysis</div>', unsafe_allow_html=True)

# ─── Bottom row: Service heatmap + Alert distribution ────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
b1, b2, b3 = st.columns([2, 1.5, 1.5])

with b1:
    st.markdown('<div class="section-header">🌡️ Service × Level Heatmap</div>', unsafe_allow_html=True)
    if len(df_win) > 0:
        heatmap_df = df_win.groupby(["service","level"]).size().unstack(fill_value=0)
        for col in ["INFO","WARN","ERROR","CRITICAL"]:
            if col not in heatmap_df.columns:
                heatmap_df[col] = 0
        heatmap_df = heatmap_df[["INFO","WARN","ERROR","CRITICAL"]]
        fig4 = go.Figure(go.Heatmap(
            z=heatmap_df.values,
            x=heatmap_df.columns.tolist(),
            y=heatmap_df.index.tolist(),
            colorscale=[[0,"#1a1f2e"],[0.3,"#1e3a5f"],[0.6,"#f97316"],[1,"#ef4444"]],
            text=heatmap_df.values,
            texttemplate="%{text}",
            showscale=False,
        ))
        fig4.update_layout(
            paper_bgcolor="#1a1f2e", plot_bgcolor="#1a1f2e",
            font=dict(color="#94a3b8", size=11),
            margin=dict(l=10,r=10,t=10,b=10),
            height=200,
            xaxis=dict(color="#94a3b8"),
            yaxis=dict(color="#94a3b8", tickfont=dict(size=9)),
        )
        st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar":False})

with b2:
    st.markdown('<div class="section-header">📊 Alert Severity Mix</div>', unsafe_allow_html=True)
    if st.session_state.alert_history:
        sev_counts = {}
        for a in st.session_state.alert_history:
            sev_counts[a["severity"]] = sev_counts.get(a["severity"],0) + 1
        fig5 = go.Figure(go.Pie(
            labels=list(sev_counts.keys()),
            values=list(sev_counts.values()),
            hole=0.55,
            marker_colors=[SEV_COLOR.get(k,"#888") for k in sev_counts.keys()],
            textfont=dict(color="#e2e8f0", size=11),
        ))
        fig5.update_layout(
            paper_bgcolor="#1a1f2e",
            font=dict(color="#94a3b8"),
            margin=dict(l=10,r=10,t=10,b=10),
            legend=dict(bgcolor="#1a1f2e", font=dict(size=10)),
            height=200,
            showlegend=True,
        )
        st.plotly_chart(fig5, use_container_width=True, config={"displayModeBar":False})
    else:
        st.markdown('<div style="height:200px;display:flex;align-items:center;justify-content:center;color:#475569;font-size:0.8rem;">No alerts yet</div>', unsafe_allow_html=True)

with b3:
    st.markdown('<div class="section-header">🌐 Top IPs by Volume</div>', unsafe_allow_html=True)
    if len(df_win) > 0:
        top_ips = df_win.groupby("ip_address").size().sort_values(ascending=False).head(6).reset_index()
        top_ips.columns = ["ip","count"]
        max_count = top_ips["count"].max()
        for _, row in top_ips.iterrows():
            pct = int(row["count"] / max(max_count,1) * 100)
            is_suspect = row["ip"] in [ATTACKER_IP, BOT_IP]
            color = "#ef4444" if is_suspect else "#3b82f6"
            flag = " 🚨" if is_suspect else ""
            st.markdown(f"""
            <div style="margin-bottom:0.4rem;">
                <div style="display:flex;justify-content:space-between;font-size:0.72rem;font-family:JetBrains Mono;color:#94a3b8;">
                    <span>{row['ip']}{flag}</span><span style="color:{color}">{row['count']}</span>
                </div>
                <div style="background:#1e293b;height:4px;border-radius:2px;margin-top:0.15rem;">
                    <div style="background:{color};height:4px;border-radius:2px;width:{pct}%;"></div>
                </div>
            </div>""", unsafe_allow_html=True)

# ─── Auto-refresh ──────────────────────────────────────────────────────────────
if st.session_state.sim_running:
    time.sleep(1.5)
    st.rerun()