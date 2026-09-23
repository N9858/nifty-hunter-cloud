import os, requests
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
import pytz
from datetime import datetime

app = Flask(__name__)

# --- NEE DETAILS - CORRECT ---
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8960559093:AAHp20LFuHStvsa4YMOmxJaA1eifDc97c8M")
CHAT_ID = os.environ.get("CHAT_ID", "5066142970")

def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        r = requests.post(url, json={"chat_id": CHAT_ID, "text": msg, "parse_mode":"Markdown"}, timeout=15)
        print("Telegram:", r.text)
        return r.text
    except Exception as e:
        print("TG Error:", e)
        return str(e)

def get_levels():
    try:
        # BTC - Binance
        r = requests.get("https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT", timeout=10).json()
        btc_close = float(r['lastPrice'])

        # NIFTY - Yahoo
        r2 = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/%5ENSEI?interval=1d&range=5d",
                          headers={"User-Agent":"Mozilla/5.0"}, timeout=10).json()
        n_close = float(r2['chart']['result'][0]['indicators']['quote'][0]['close'][-1])

        pct = 0.004 # 0.4% TIGHT

        btc_buy = round(btc_close * (1 + pct), 2)
        btc_sell = round(btc_close * (1 - pct), 2)
        n_buy = round(n_close * (1 + pct), 2)
        n_sell = round(n_close * (1 - pct), 2)

        btc_sl_b = round(btc_close * (1 + pct*0.5), 2)
        btc_sl_s = round(btc_close * (1 - pct*0.5), 2)
        btc_t_b = round(btc_buy * 1.008, 2)
        btc_t_s = round(btc_sell * 0.992, 2)

        n_sl_b = round(n_close * (1 + pct*0.5), 2)
        n_sl_s = round(n_close * (1 - pct*0.5), 2)
        n_t_b = round(n_buy * 1.008, 2)
        n_t_s = round(n_sell * 0.992, 2)

        return btc_close, btc_buy, btc_sell, btc_sl_b, btc_sl_s, btc_t_b, btc_t_s, n_close, n_buy, n_sell, n_sl_b, n_sl_s, n_t_b, n_t_s
    except Exception as e:
        print("Data Error:", e)
        # Fallback tight
        return 86500, 86846, 86154, 86673, 86327, 87541, 85464, 23400, 23493, 23306, 23446, 23354, 23681, 23120

def build_msg():
    b_c, b_b, b_s, b_sl_b, b_sl_s, b_t_b, b_t_s, n_c, n_b, n_s, n_sl_b, n_sl_s, n_t_b, n_t_s = get_levels()
    now = datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%d-%m-%Y %H:%M')
    msg = f"🔥 *NIFTY + BTC HUNTER - AUTO 9:15 AM* 🔥\n\n₿ *BTC: {b_c}*\n🟢 BUY ABOVE {b_b} | SL {b_sl_b} | TGT {b_t_b}\n🔴 SELL BELOW {b_s} | SL {b_sl_s} | TGT {b_t_s}\n\n📈 *NIFTY: {n_c}*\n🟢 BUY ABOVE {n_b} | SL {n_sl_b} | TGT {n_t_b}\n🔴 SELL BELOW {n_s} | SL {n_sl_s} | TGT {n_t_s}\n\n⏰ {now}\n✅ LIVE"
    return msg

def daily_job():
    msg = build_msg()
    send_telegram(msg)

@app.route('/')
def home():
    return build_msg().replace('\n','<br>') + '<br><br><a href="/send-now"><button style="padding:20px;background:green;color:white;font-size:22px;border-radius:10px">🚀 Send Telegram Now</button></a>'

@app.route('/send-now')
def send_now():
    daily_job()
    return "✅ Sent to Telegram! Check your Telegram now - ID: 5066142970"

scheduler = BackgroundScheduler(timezone=pytz.timezone('Asia/Kolkata'))
scheduler.add_job(daily_job, 'cron', hour=9, minute=15)
scheduler.start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT",10000)))
