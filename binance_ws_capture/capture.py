import websocket, json, gzip, time, datetime as dt
from pathlib import Path
from orderbook import OrderBook

Path("data").mkdir(exist_ok=True)
filename = f"data/btcusdt_{dt.datetime.utcnow().isoformat()}.jsonl.gz"

book = OrderBook()                   # integrity check in parallel

def on_message(_, raw):
    payload = {"ts": time.time_ns(), "data": json.loads(raw)}
    # ---- live integrity check (doesn't affect file write) ----
    book.apply_delta(payload["data"])

    # ---- persist raw message ----
    with gzip.open(filename, "at") as f:
        f.write(json.dumps(payload) + "\n")

def on_error(_, err):   print("[ERROR]", err)
def on_close(_, c, m):  print("[CLOSE]", c, m)

# use generic endpoint → need explicit SUBSCRIBE to depth + trades
url = "wss://stream.binance.us:9443/ws"
def on_open(ws):
    sub = {
        "method": "SUBSCRIBE",
        "params": [
            "btcusdt@depth@100ms",        # depth deltas
            "btcusdt@aggTrade"            # trades
        ],
        "id": 1
    }
    ws.send(json.dumps(sub))
    print("[OPEN] subscribed")

ws = websocket.WebSocketApp(
    url,
    on_open=on_open,
    on_message=on_message,
    on_error=on_error,
    on_close=on_close,
)
ws.run_forever()
