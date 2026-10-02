import requests
import time
import os
from flask import Flask
import threading

# --- FLASK FOR RENDER PORT ---
flask_app = Flask(__name__)
@flask_app.route('/')
def home():
    return "Bot is Running! LIVE NIFTY Tracker"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host='0.0.0.0', port=port)

threading.Thread(target=run_flask, daemon=True).start()
# -----------------------------

TOKEN = os.environ.get("8742634693:AAFg-Kj8kb3COA1Dv-FqXSvOlyD75zt3mzc")
CHAT_ID = os.environ.get("5066142970")

NO_LOW = 22400
NO_HIGH = 22450
BUY_LEVEL = 22500
SELL_LEVEL = 22350

def send_telegram(msg):
    if not TOKEN or not CHAT_ID:
        print("Token/Chat ID missing in Env Vars!")
        return
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.get(url, params={"chat_id": CHAT_ID, "text": msg})
    except Exception as e:
        print(f"Telegram Error: {e}")

while True:
    try:
        r = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/%5ENSEI?interval=1m", headers={'User-Agent': 'Mozilla/5.0'}).json()
        price = r['chart']['result'][0]['meta']['regularMarketPrice']
        now = time.strftime('%H:%M:%S')
        print(f"LIVE NIFTY: {price} | {now}")

        if NO_LOW < price < NO_HIGH:
            print(f"--> NO TRADE ZONE {NO_LOW}-{NO_HIGH}")
        elif price >= BUY_LEVEL:
            msg = f"🟢 BUY BREAKOUT! Nifty {price} -> Above {BUY_LEVEL}"
            print(msg)
            send_telegram(msg)
            time.sleep(300)
        elif price <= SELL_LEVEL:
            msg = f"🔴 SELL BREAKDOWN! Nifty {price} -> Below {SELL_LEVEL}"
            print(msg)
            send_telegram(msg)
            time.sleep(300)
        else:
            print("--> Waiting for level...")
        time.sleep(60)
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(60)
