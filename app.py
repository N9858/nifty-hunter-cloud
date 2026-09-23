import os, requests
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
import pytz
from datetime import datetime

app = Flask(__name__)
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def send_telegram(msg):
    if not BOT_TOKEN or not CHAT_ID: return
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except: pass

def get_levels():
    try:
        r = requests.get("https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1d&limit=5", timeout=10).json()
        btc_close = float(r[-1][4])
        btc_pct = 0.004
        btc_buy = round(btc_close * (1 + btc_pct), 2)
        btc_sell = round(btc_close * (1 - btc_pct), 2)
        btc_sl_buy = round(btc_close * (1 + btc_pct*0.6), 2)
        btc_sl_sell = round(btc_close * (1 - btc_pct*0.6), 2)
        btc_tgt_buy = round(btc_buy * 1.008, 2)
        btc_tgt_sell = round(btc_sell * 0.992, 2)

        r2 = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/%5ENSEI?interval=1d&range=5d", headers={"User-Agent":"Mozilla/5.0"}, timeout=10).json()
        n_close = float(r2['chart']['result'][0]['indicators']['quote'][0]['close'][-1])
        n_pct = 0.004
        n_buy = round(n_close * (1 + n_pct), 2)
        n_sell = round(n_close * (1 - n_pct), 2)
        n_sl_buy = round(n_close * (1 + n_pct*0.6), 2)
        n_sl_sell = round(n_close * (1 - n_pct*0.6), 2)
        n_tgt_buy = round(n_buy * 1.008, 2)
        n_tgt_sell = round(n_sell * 0.992, 2)

        return btc_close, btc_buy, btc_sell, btc_sl_buy, btc_sl_sell, btc_tgt_buy, btc_tgt_sell, n_close, n_buy, n_sell, n_sl_buy, n_sl_sell, n_tgt_buy, n_tgt_sell
    except Exception as e:
        print(e)
        return 86000, 86344, 85656, 86200, 85800, 87000, 85000, 23400, 23493, 23306, 23456, 23344, 23681, 23120

def build_msg():
    b_c, b_b, b_s, b_sl_b, b_sl_s, b_t_b, b_t_s, n_c, n_b, n_s, n_sl_b, n_sl_s, n_t_b, n_t_s = get_levels()
    now = datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%d-%m-%Y %H:%M')
    msg = f"🔥 NIFTY + BTC HUNTER - AUTO 9:15 AM 🔥\n\n₿ BTC: {b_c}\n🟢 BUY ABOVE {b_b} | SL {b_sl_b} | TGT {b_t_b}\n🔴 SELL BELOW {b_s} | SL {b_sl_s} | TGT {b_t_s}\n\n📈 NIFTY: {n_c}\n🟢 BUY ABOVE {n_b} | SL {n_sl_b} | TGT {n_t_b}\n🔴 SELL BELOW {n_s} | SL {n_sl_s} | TGT {n_t_s}\n\n⏰ {now}"
    return msg

def daily_job():
    send_telegram(build_msg())

@app.route('/')
def home():
    return build_msg().replace('\n','<br>') + '<br><br><a href="/send-now"><button style="padding:15px;background:green;color:white;font-size:20px">Send Telegram Now</button></a>'

@app.route('/send-now')
def send_now():
    daily_job()
    return "Sent! Check Telegram"

scheduler = BackgroundScheduler(timezone=pytz.timezone('Asia/Kolkata'))
scheduler.add_job(daily_job, 'cron', hour=9, minute=15)
scheduler.start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT",10000)))
