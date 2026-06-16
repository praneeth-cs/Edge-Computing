import streamlit as st
import pandas as pd
import asyncio
import websockets
import json
from datetime import datetime
import threading
import queue

# ================= CONFIG =================

PORT = 8765
SESSION_TIMEOUT = 30
REFRESH_INTERVAL = 3

# ================= GLOBAL QUEUE =================

if "data_queue" not in st.session_state:
    st.session_state.data_queue = queue.Queue()

if "active_sessions" not in st.session_state:
    st.session_state.active_sessions = {}

if "history_sessions" not in st.session_state:
    st.session_state.history_sessions = {}

# ================= WEBSOCKET SERVER =================

async def websocket_handler(websocket):
    async for message in websocket:
        data = json.loads(message)
        st.session_state.data_queue.put(data)

async def start_server():
    async with websockets.serve(websocket_handler, "0.0.0.0", PORT):
        await asyncio.Future()

def run_server():
    asyncio.run(start_server())

if "server_started" not in st.session_state:
    threading.Thread(target=run_server, daemon=True).start()
    st.session_state.server_started = True

# ================= PROCESS INCOMING DATA =================

while not st.session_state.data_queue.empty():
    data = st.session_state.data_queue.get()

    device = data.get("device_id")
    session = data.get("session_id")
    key = f"{device}_{session}"

    st.session_state.active_sessions[key] = {
        "device": device,
        "session": session,
        "label": data.get("label"),
        "confidence": data.get("confidence"),
        "last_update": datetime.utcnow()
    }

# ================= CLEANUP =================

now = datetime.utcnow()
to_remove = []

for key, value in st.session_state.active_sessions.items():
    if (now - value["last_update"]).total_seconds() > SESSION_TIMEOUT:
        st.session_state.history_sessions[key] = value
        to_remove.append(key)

for key in to_remove:
    del st.session_state.active_sessions[key]

# ================= DASHBOARD =================

st.set_page_config(layout="wide")
st.title("Edge Object Detection Monitor")

st.header("Active Sessions")

if st.session_state.active_sessions:
    df_active = pd.DataFrame([
        {
            "Device": v["device"],
            "Session": v["session"],
            "Label": v["label"],
            "Confidence": round(v["confidence"], 2),
            "Last Update (UTC)": v["last_update"].strftime("%H:%M:%S")
        }
        for v in st.session_state.active_sessions.values()
    ])
    st.dataframe(df_active, use_container_width=True)
else:
    st.info("No active sessions.")

st.header("Past Sessions")

if st.session_state.history_sessions:
    df_history = pd.DataFrame([
        {
            "Device": v["device"],
            "Session": v["session"],
            "Final Label": v["label"],
            "Final Confidence": round(v["confidence"], 2)
        }
        for v in st.session_state.history_sessions.values()
    ])
    st.dataframe(df_history, use_container_width=True)
else:
    st.info("No past sessions.")

st.caption(f"Auto-refresh every {REFRESH_INTERVAL} seconds.")

st.experimental_rerun() if False else None
