import json
import csv
import threading
from collections import deque

import certifi
import websocket
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter, MaxNLocator
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d.art3d import Line3DCollection

URL = "wss://data-stream.binance.vision/ws/btcusdt@trade"
MAX_POINTS = 1000
MIN_PRICE_RANGE = 2.0

times = deque(maxlen=MAX_POINTS)
prices = deque(maxlen=MAX_POINTS)
qtys = deque(maxlen=MAX_POINTS)
sides = deque(maxlen=MAX_POINTS)
lock = threading.Lock()

file = open("btc_trades.csv", "a", newline="")
writer = csv.writer(file)

def on_open(ws):
    print("connected")

def on_error(ws, error):
    print("error:", error)

def on_message(ws, message):
    t = json.loads(message)
    with lock:
        times.append(t["T"])
        prices.append(float(t["p"]))
        qtys.append(float(t["q"]))
        sides.append(t["m"])
    writer.writerow([t["T"], t["p"], t["q"], t["m"]])
    file.flush()

ws = websocket.WebSocketApp(URL, on_open=on_open, on_message=on_message, on_error=on_error)
thread = threading.Thread(
    target=ws.run_forever,
    kwargs={"reconnect": 5, "sslopt": {"ca_certs": certifi.where()}},
    daemon=True,
)
thread.start()

fig = plt.figure(figsize=(11, 7))
ax = fig.add_subplot(projection="3d")
ax.view_init(elev=20, azim=-50)

def update(frame):
    with lock:
        x = list(times)
        y = list(prices)
        z = list(qtys)
        m = list(sides)
    if not y:
        return
    elev, azim = ax.elev, ax.azim
    ax.cla()

    t0 = x[0]
    xs = [(ti - t0) / 1000 for ti in x]
    colors = ["red" if s else "green" for s in m]

    stems = [[(xi, yi, 0), (xi, yi, zi)] for xi, yi, zi in zip(xs, y, z)]
    ax.add_collection3d(Line3DCollection(stems, colors=colors, linewidths=1.5, alpha=0.8))
    ax.scatter(xs, y, z, c=colors, s=12, depthshade=False)

    mid = (max(y) + min(y)) / 2
    half = max((max(y) - min(y)) / 2, MIN_PRICE_RANGE / 2)
    ax.set_xlim(0, max(xs[-1], 1))
    ax.set_ylim(mid - half, mid + half)
    ax.set_zlim(0, max(z) * 1.1)

    ax.yaxis.set_major_formatter(FormatStrFormatter("%.2f"))
    ax.yaxis.set_major_locator(MaxNLocator(5))
    ax.set_xlabel("Время, секунды", labelpad=10)
    ax.set_ylabel("Цена, $", labelpad=18)
    ax.set_zlabel("Объём, BTC", labelpad=8)
    ax.set_title(f"BTC/USDT (Binance)  {y[-1]:,.2f} $   сделок: {len(y)}\n"
                 f"зелёный = покупка, красный = продажа")
    ax.view_init(elev=elev, azim=azim)

anim = FuncAnimation(fig, update, interval=500, cache_frame_data=False)
plt.show()