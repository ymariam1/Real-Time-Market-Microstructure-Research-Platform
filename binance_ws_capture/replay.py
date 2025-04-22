import gzip
import json
import time
import argparse
from strategies.naive_mm import NaiveMarketMaker


def replay(file_path, speed=1.0, on_tick=None):
    with gzip.open(file_path, 'rt') as f:
        prev_ts = None
        for line in f:
            entry = json.loads(line)
            ts = entry["ts"]
            data = entry["data"]

            if prev_ts is not None and speed > 0:
                delay_ns = ts - prev_ts
                time.sleep(delay_ns / 1e9 / speed)

            if on_tick:
                on_tick(ts, data)

            prev_ts = ts

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Path to .jsonl.gz file")
    parser.add_argument("--speed", type=float, default=1.0, help="Playback speed (1.0 = real-time)")
    args = parser.parse_args()
    mm = NaiveMarketMaker()
    replay(args.file, args.speed, on_tick=mm.on_tick)