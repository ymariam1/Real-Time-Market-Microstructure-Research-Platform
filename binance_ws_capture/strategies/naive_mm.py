import numpy as np
import collections

class NaiveMarketMaker:
    def __init__(self, spread_threshold=0.0001):
        self.spread_threshold = spread_threshold
        self.inventory = 0
        self.max_inventory = 5
        self.cash = 0
        self.inventory = 0.0
        self.orders = []  # track active orders
        self.prev_mark = None
        self.returns = collections.deque(maxlen=300)

    def on_tick(self, ts, data):
        if "bids" not in data or "asks" not in data:
            return
        best_bid = float(data['bids'][0][0])
        best_ask = float(data['asks'][0][0])
        mark     = (best_bid + best_ask) / 2
        spread   = (best_ask - best_bid) / best_bid

        if self.prev_mark:
            self.returns.append(np.log(mark / self.prev_mark))
        self.prev_mark = mark
        sigma = np.std(self.returns) if self.returns else 0.0


        # Only place orders if spread is attractive and inventory is manageable
        if spread > self.spread_threshold and abs(self.inventory) < self.max_inventory:
            bid_price = best_bid + 0.01  # slightly better than current best bid
            ask_price = best_ask - 0.01  # slightly better than current best ask
            self.orders.append({'side': 'buy', 'price': bid_price, 'ts': ts})
            self.orders.append({'side': 'sell', 'price': ask_price, 'ts': ts})

        # Check if your existing orders would realistically fill
        filled_orders = []
        for order in self.orders:
            if order['side'] == 'buy' and best_ask <= order['price']:
                self.inventory += 1
                self.cash -= order['price']
                filled_orders.append(order)
                print(f"[BUY FILL] {ts}: Filled at {order['price']:.2f}, Inventory: {self.inventory}")

            elif order['side'] == 'sell' and best_bid >= order['price']:
                self.inventory -= 1
                self.cash += order['price']
                filled_orders.append(order)
                print(f"[SELL FILL] {ts}: Filled at {order['price']:.2f}, Inventory: {self.inventory}")

        # Remove filled orders
        for order in filled_orders:
            self.orders.remove(order)
        # Track PnL   
        realised    = self.cash
        unrealised  = self.inventory * spread
        pnl         = realised + unrealised
        inv_risk    = abs(self.inventory) * sigma

        print(f"{ts}  pnl={pnl:,.8f}  inv={self.inventory:.4f}  risk={inv_risk:,.2f}")
