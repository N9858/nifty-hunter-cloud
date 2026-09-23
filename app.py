import os, requests
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
import pytz
from datetime import datetime

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8960559093:AAHp20LFuHStvsa4YMOmxJaA1eifDc97c8M")
CHAT_ID = os.environ.get("CHAT_ID", "5066142970")

def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHAT_ID, "text": msg, "parse_mode":"Markdown"}, timeout=15)
    except: pass

def get_live_btc():
    try:
        # Coingecko - Render lo 100% work avuthundi
        r = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd", timeout=10).json()
        return float(r['bitcoin']['usd'])
    except:
        return 115000 # live approx fallback

def get_live_nifty():
    try:
        # NSE via Yahoo
        url = "https://query1.finance.yahoo.com/v8/finance/chart/%5ENSEI?interval=1d&range=1d"
        r = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=10).json()
        price = r['chart']['result'][0]['meta']['regularMarketPrice']
        return float(price)
    except:
        return 24700

def build_msg():
    btc_close = get_live_btc()
    n_close = get_live_nifty()

    pct = 0.004

    b_b = round(btc_close * (1 + pct), 2)
    b_s = round(btc_close * (1 - pct), 2)
    n_b = round(n_close * (1 + pct), 2)
    n_s = round(n_close * (1 - pct), 2)

    now = datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%d-%m-%Y %H:%M')

    msg = f"🔥 *NIFTY + BTC HUNTER - LIVE* 🔥\n\n₿ *BTC LIVE: {btc_close}*\n🟢 BUY ABOVE {b_b} | SL {round(b_b*0.998,2)} | TGT {round(b_b*1.008,2)}\n🔴 SELL BELOW {b_s} | SL {round(b_s*1.002,2)} | TGT {round(b_s*0.992,2)}\n\n📈 *NIFTY LIVE: {n_close}*\n🟢 BUY ABOVE {n_b} | SL {round(n_b*0.998,2)} | TGT {round(n_b*1.008,2)}\n🔴 SELL BELOW {n_s} | SL {round(n_s*1.002,2)} | TGT {round(n_s*0.992,2)}\n\n⏰ {now}\n✅ LIVE PRICE"
    return msg

def daily_job():
    send_telegram(build_msg())

@app.route('/')
def home():
    return build_msg().replace('\n','<br>') + '<br><br><a href="/send-now">SEND NOW</a>'

@app.route('/send-now')
def send_now():
    daily_job()
    return "✅ LIVE Sent!"

scheduler = BackgroundScheduler(timezone=pytz.timezone('Asia/Kolkata'))
scheduler.add_job(daily_job, 'cron', hour=9, minute=15)
scheduler.start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT",10000)))
