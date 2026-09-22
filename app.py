from flask import Flask
import yfinance as yf
import requests, threading, time
from datetime import datetime

app = Flask(__name__)

BOT_TOKEN = "8960559093:AAFCsaeOu4PsSRY4QKAKAAJyyTcImkVagZw"
CHAT_ID = "5066142970"

def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        r = requests.post(url, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"})
        print(r.text)
        return r.text
    except Exception as e:
        return str(e)

def get_levels(symbol):
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="1d", interval="15m")
        if df.empty: return None
        high = df['High'].max(); low = df['Low'].min(); close = df['Close'].iloc[-1]
        return {
            "close": round(close,2),
            "buy": round(high,2), "buy_sl": round(high*0.9985,2), "buy_tgt": round(high*1.003,2),
            "sell": round(low,2), "sell_sl": round(low*1.0015,2), "sell_tgt": round(low*0.997,2)
        }
    except: return None

@app.route("/")
def home():
    btc = get_levels("BTC-USD"); nifty = get_levels("^NSEI")
    def card(title, d, color):
        if not d: return ""
        return f"<div style='background:#111;padding:15px;border-radius:10px;margin:10px;border-left:4px solid {color}'><h3>{title}: {d['close']}</h3><p style='color:#00ff88'>🟢 BUY ABOVE {d['buy']} | SL {d['buy_sl']} | TGT {d['buy_tgt']}</p><p style='color:#ff4444'>🔴 SELL BELOW {d['sell']} | SL {d['sell_sl']} | TGT {d['sell_tgt']}</p></div>"
    return f"<body style='background:#000;color:#fff;font-family:Arial;padding:20px'><h1 style='text-align:center'>🔥 NIFTY + BTC HUNTER 🔥</h1>{card('₿ BTC',btc,'#f7931a')}{card('📈 NIFTY',nifty,'#00ff88')}<p style='text-align:center'><a href='/send_now' style='background:#0088cc;color:white;padding:12px 20px;border-radius:8px;text-decoration:none'>📩 Send Telegram Now</a></p><p style='text-align:center;color:#888'>{datetime.now()}</p></body>"

@app.route("/send_now")
def send_now():
    btc = get_levels("BTC-USD"); nifty = get_levels("^NSEI")
    msg = f"🔥 <b>NIFTY + BTC UPDATE</b> 🔥\n⏰ {datetime.now().strftime('%d-%m %H:%M')}\n\n"
    if btc: msg += f"₿ <b>BTC: ${btc['close']}</b>\n🟢 BUY {btc['buy']} | SL {btc['buy_sl']} | TGT {btc['buy_tgt']}\n🔴 SELL {btc['sell']} | SL {btc['sell_sl']} | TGT {btc['sell_tgt']}\n\n"
    if nifty: msg += f"📈 <b>NIFTY: {nifty['close']}</b>\n🟢 BUY {nifty['buy']} | SL {nifty['buy_sl']} | TGT {nifty['buy_tgt']}\n🔴 SELL {nifty['sell']} | SL {nifty['sell_sl']} | TGT {nifty['sell_tgt']}"
    result = send_telegram(msg)
    return f"Telegram API Response:<br>{result}<br><br>Message:<br>{msg.replace(chr(10),'<br>')}"

# auto every 1 hour
def auto_sender():
    while True:
        time.sleep(3600)
        try:
            btc = get_levels("BTC-USD"); nifty = get_levels("^NSEI")
            if btc: send_telegram(f"⏰ AUTO ₿ BTC ${btc['close']} BUY {btc['buy']} SELL {btc['sell']}")
        except: pass
threading.Thread(target=auto_sender, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
