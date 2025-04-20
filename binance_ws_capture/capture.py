import websocket
import json
import gzip
import time
import datetime as dt
from pathlib import Path

Path("data").mkdir(parents=True, exist_ok=True)
filename = f"data/btcusdt_{dt.datetime.utcnow().isoformat()}.jsonl.gz"

def on_message(ws, message):
    with gzip.open(filename, 'at') as f:
        payload = {
            "ts": time.time_ns(),
            "data": json.loads(message)
        }
        f.write(json.dumps(payload) + "\n")

def on_error(ws, error):
    print(f"[ERROR] {error}")

def on_close(ws, close_status_code, close_msg):
    print(f"[CLOSED] code={close_status_code}, msg={close_msg}")


def on_open(ws):
    print("[OPEN] WebSocket connection opened")
    subscribe_message = {
        "method": "SUBSCRIBE",
        "params": [
            "btcusdt@depth@100ms",
            "btcusdt@aggTrade"
        ],
        "id": 1
    }
    print("[SEND] Subscribing to streams")
    ws.send(json.dumps(subscribe_message))

ws = websocket.WebSocketApp(
    "wss://stream.binance.us:9443/ws/btcusdt@depth10@100ms",
    on_message=on_message,
    on_error=on_error,
    on_close=on_close,
    on_open=on_open
)

ws.run_forever()