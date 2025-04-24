import requests

class OrderBook:
    SNAP_URL = "https://api.binance.us/api/v3/depth"
    PARAMS   = {"symbol": "BTCUSDT", "limit": 1000}

    def __init__(self):
        self.bids = {}
        self.asks = {}
        self.last_update_id = None
        self.resync()                 # fetch initial snapshot

    def resync(self):
        snap = requests.get(self.SNAP_URL, params=self.PARAMS, timeout=5).json()
        self.last_update_id = snap["lastUpdateId"]
        self.bids = {float(p): float(q) for p, q in snap["bids"]}
        self.asks = {float(p): float(q) for p, q in snap["asks"]}
        print("[SYNC] snapshot id:", self.last_update_id)

    def apply_delta(self, msg):
        # depth messages have keys b / a / U / u
        if "b" not in msg or "a" not in msg:
            return False             # ignore trades etc.

        first, last = msg["U"], msg["u"]

        # too old → ignore
        if last <= self.last_update_id:
            return False

        # gap → resync
        if first > self.last_update_id + 1:
            print("[GAP] missed", self.last_update_id + 1, "…", first - 1)
            self.resync()
            return False

        # apply deltas
        for p, q in msg["b"]:
            p, q = float(p), float(q)
            if q == 0:
                self.bids.pop(p, None)
            else:
                self.bids[p] = q
        for p, q in msg["a"]:
            p, q = float(p), float(q)
            if q == 0:
                self.asks.pop(p, None)
            else:
                self.asks[p] = q

        self.last_update_id = last
        return True

    # helpers
    def best_bid(self):
        return max(self.bids) if self.bids else None
    def best_ask(self):
        return min(self.asks) if self.asks else None
