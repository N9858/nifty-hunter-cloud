from flask import Flask
import os, requests

app = Flask(__name__)

@app.route("/")
def home():
    return "NIFTY HUNTER LIVE! /check kottu"

@app.route("/check")
def check():
    TELE_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    ACCESS_TOKEN = os.getenv("UPSTOX_ACCESS_TOKEN")
    
    # Nifty Price
    try:
        h = {'Authorization': f'Bearer {ACCESS_TOKEN}'}
        url = "https://api.upstox.com/v2/market-quote/ltp?instrument_key=NSE_INDEX|Nifty 50"
        price = requests.get(url, headers=h, timeout=10).json()['data']['NSE_INDEX:Nifty 50']['last_price']
    except:
        return "Upstox Token Expired - Update Token"

    atm = int(round(price/50)*50)
    msg = f"✅ NIFTY LIVE {price}\n🟢 BUY {atm} CE\nTarget {price+80}\nSL {price-60}"
    
    # Telegram
    try:
        t_url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
        requests.post(t_url, data={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except: pass
    
    return msg

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
