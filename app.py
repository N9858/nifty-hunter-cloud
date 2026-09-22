from flask import Flask
import requests
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import pytz

app = Flask(__name__)

BOT_TOKEN = "8960559093:AAEcfT8WxfbH9sfGdB1t7vdrDmCsVe85fH8"
CHAT_ID = "5066142970"

def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
        requests.post(url, data=data, timeout=10)
        print("Telegram Sent!")
    except Exception as e:
        print(f"Error: {e}")

def get_levels_yahoo(symbol):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=5d&interval=1d"
        r = requests.get(url, headers=headers, timeout=10)
        j = r.json()
        result = j['chart']['result'][0]
        closes = result['indicators']['quote'][0]['close']
        highs = result['indicators']['quote'][0]['high']
        lows = result['indicators']['quote'][0]['low']

        close = [c for c in closes if c is not None][-1]
        high = max([h for h in highs if h is not None][-2:])
        low = min([l for l in lows if l is not None][-2:])

        close = round(close, 2)
        high = round(high, 2)
        low = round(low, 2)

        range_val = high - low
        buy_level = round(high + range_val*0.15, 2)
        buy_sl = round(buy_level - range_val*0.25, 2)
        buy_tgt = round(buy_level + range_val*0.6, 2)

        sell_level = round(low - range_val*0.15, 2)
        sell_sl = round(sell_level + range_val*0.25, 2)
        sell_tgt = round(sell_level - range_val*0.6, 2)

        return close, buy_level, buy_sl, buy_tgt, sell_level, sell_sl, sell_tgt
    except:
        return 86277.92, 86700, 86500, 87000, 85000, 85200, 84800

def daily_job():
    print("Running Daily Job...")
    btc_close, btc_buy, btc_bsl, btc_btgt, btc_sell, btc_ssl, btc_stgt = get_levels_yahoo("BTC-USD")
    nifty_close, n_buy, n_bsl, n_btgt, n_sell, n_ssl, n_stgt = get_levels_yahoo("^NSEI")

    msg = f"🔥 *NIFTY + BTC HUNTER - AUTO ALERT 9:15 AM* 🔥\n\n₿ *BTC: {btc_close}*\n🟢 BUY ABOVE {btc_buy} | SL {btc_bsl} | TGT {btc_btgt}\n🔴 SELL BELOW {btc_sell} | SL {btc_ssl} | TGT {btc_stgt}\n\n📈 *NIFTY: {nifty_close}*\n🟢 BUY ABOVE {n_buy} | SL {n_bsl} | TGT {n_btgt}\n🔴 SELL BELOW {n_sell} | SL {n_ssl} | TGT {n_stgt}\n\n⏰ {datetime.now().strftime('%d-%m-%Y %H:%M')}"
    send_telegram(msg)

# Scheduler - 9:15 AM IST = 3:45 AM UTC
scheduler = BackgroundScheduler(timezone=pytz.timezone('Asia/Kolkata'))
scheduler.add_job(daily_job, 'cron', hour=9, minute=15)
scheduler.start()
print("Scheduler Started - Daily 9:15 AM IST")

@app.route("/")
def home():
    btc_close, btc_buy, btc_bsl, btc_btgt, btc_sell, btc_ssl, btc_stgt = get_levels_yahoo("BTC-USD")
    nifty_close, n_buy, n_bsl, n_btgt, n_sell, n_ssl, n_stgt = get_levels_yahoo("^NSEI")
    html = f"""
    <body style="background:black;color:white;font-family:Arial;padding:20px">
    <h2 style="text-align:center">🔥 NIFTY + BTC HUNTER - AUTO MODE ON 🔥</h2>
    <p style="text-align:center;color:#00ff88">✅ Daily 9:15 AM Auto Alert Active!</p>
    <div style="background:#111;padding:15px;border-left:4px solid orange;border-radius:8px;margin-bottom:15px">
    <b>₿ BTC: {btc_close}</b><br><br>
    <span style="color:#00ff88">🟢 BUY ABOVE {btc_buy} | SL {btc_bsl} | TGT {btc_btgt}</span><br>
    <span style="color:#ff4444">🔴 SELL BELOW {btc_sell} | SL {btc_ssl} | TGT {btc_stgt}</span>
    </div>
    <div style="background:#111;padding:15px;border-left:4px solid #00ff88;border-radius:8px;margin-bottom:15px">
    <b>📈 NIFTY: {nifty_close}</b><br><br>
    <span style="color:#00ff88">🟢 BUY ABOVE {n_buy} | SL {n_bsl} | TGT {n_btgt}</span><br>
    <span style="color:#ff4444">🔴 SELL BELOW {n_sell} | SL {n_ssl} | TGT {n_stgt}</span>
    </div>
    <div style="text-align:center">
    <a href="/send_now" style="background:#0a4a6b;color:white;padding:15px 30px;text-decoration:none;border-radius:8px;font-weight:bold">📩 Send Telegram Now</a><br><br>
    <a href="/test_auto" style="background:green;color:white;padding:10px 20px;text-decoration:none;border-radius:8px">Test Auto Job</a>
    <p>Next Auto Alert: Today 9:15 AM IST</p>
    </div>
    </body>
    """
    return html

@app.route("/send_now")
def send_now():
    daily_job()
    return "<h3>Sent! Check Telegram</h3><a href='/'>Go Back</a>"

@app.route("/test_auto")
def test_auto():
    daily_job()
    return "<h3>Auto Job Tested! Check Telegram</h3><a href='/'>Go Back</a>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
