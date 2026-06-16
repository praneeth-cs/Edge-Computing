import asyncio
import websockets
import json
from datetime import datetime, timedelta

active_sessions = {}
history_sessions = []

SESSION_TIMEOUT = 30  # seconds


def cleanup_sessions():
    now = datetime.utcnow()
    to_remove = []

    for key, value in active_sessions.items():
        last_update = datetime.fromisoformat(value["last_update"])
        if (now - last_update).total_seconds() > SESSION_TIMEOUT:
            history_sessions.append(value)
            to_remove.append(key)

    for key in to_remove:
        del active_sessions[key]


async def handler(websocket):
    async for message in websocket:
        data = json.loads(message)

        device = data.get("device_id")
        session = data.get("session_id")
        key = f"{device}_{session}"

        active_sessions[key] = {
            "device": device,
            "session": session,
            "label": data.get("label"),
            "confidence": data.get("confidence"),
            "last_update": datetime.utcnow().isoformat()
        }

        print("Updated:", active_sessions[key])


async def main():
    async with websockets.serve(handler, "0.0.0.0", 8765):
        print("WebSocket server started on port 8765")
        while True:
            cleanup_sessions()
            await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())
