import json
import csv
import certifi
import websocket

URL = "wss://data-stream.binance.vision/ws/btcusdt@trade"

file = open("btc_trades.csv", "a", newline="")
writer = csv.writer(file)

def on_open(ws):
    print("connected")

def on_error(ws, error):
    print("error:", error)

def on_message(ws, message):
    t = json.loads(message)
    print(t["T"], t["p"], t["q"])
    writer.writerow([t["T"], t["p"], t["q"]])
    file.flush()

ws = websocket.WebSocketApp(URL, on_open=on_open, on_message=on_message, on_error=on_error)
ws.run_forever(reconnect=5, sslopt={"ca_certs": certifi.where()})