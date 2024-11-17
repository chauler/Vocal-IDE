import os
import websocket
import json

DEFAULT_PORT = 8080


def send_message(message):
    ws = websocket.WebSocket()
    ws.connect(
        f"ws://localhost:{int(os.environ.get("SERVER_PORT", DEFAULT_PORT))}")
    ws.send(json.dumps(message))
    ws.close()
