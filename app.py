from flask import Flask
import yfinance as yf
import requests
import threading
import time
from datetime import datetime

app = Flask(__name__)

BOT_TOKEN = "8742634693:AAGglf8RKGZTMdEXXAx0ljfv2qtr5Ue1-M8"
CHAT_ID = "5066142970"

def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"})
        print("Telegram sent!")
    except Exception as e:
        print(f"Telegram error: {e}")

def get_levels(symbol):
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="1d", interval="15m")
        if df.empty:
            return None
        high = df['High'].max()
        low = df['Low'].min()
        close = df['Close'].iloc[-1]
        buy = round(high, 2)
        sell = round(low, 2)
        buy_sl = round(buy - (buy*0.0015), 2)
        buy_tgt = round(buy + (buy*0.003), 2)
        sell_sl = round(sell + (sell*0.0015), 2)
        sell_tgt = round(sell - (sell*0.003), 2)
        return {"close": round(close,2), "buy": buy, "buy_sl": buy_sl, "buy_tgt": buy_tgt, "sell": sell, "sell_sl": sell_sl, "sell_tgt": sell_tgt}
    except:
        return None

@app.route("/")
def home():
    btc = get_levels("BTC-USD")
    nifty = get_levels("^NSEI")
    
    btc_html = f"<div style='background:#111;padding:15px;border-radius:10px;margin:10px;border-left:4px solid #f7931a'><h3>₿ BTC: ${btc['close']}</h3><p style='color:#00ff88'>🟢 BUY ABOVE {btc['buy']} | SL {btc['buy_sl']} | TGT {btc['buy_tgt']}</p><p style='color:#ff4444'>🔴 SELL BELOW {btc['sell']} | SL {btc['sell_sl']} | TGT {btc['sell_tgt']}</p></div>" if btc else "<p>BTC loading...</p>"
    nifty_html = f"<div style='background:#111;padding:15px;border-radius:10px;margin:10px;border-left:4px solid #00ff88'><h3>📈 NIFTY: {nifty['close']}</h3><p style='color:#00ff88'>🟢 BUY ABOVE {nifty['buy']} | SL {nifty['buy_sl']} | TGT {nifty['buy_tgt']}</p><p style='color:#ff4444'>🔴 SELL BELOW {nifty['sell']} | SL {nifty['sell_sl']} | TGT {nifty['sell_tgt']}</p></div>" if nifty else "<p>Nifty loading...</p>"

    return f"""
    <html><head><meta name="viewport" content="width=device-width, initial-scale=1"><title>Nifty Hunter + BTC</title></head>
    <body style="background:#000;color:#fff;font-family:Arial;padding:20px">
    <h1 style="text-align:center">🔥 NIFTY + BTC HUNTER 🔥</h1>
    {btc_html}
    {nifty_html}
    <p style="text-align:center;margin-top:20px"><a href="/send_now" style="background:#0088cc;color:white;padding:12px 20px;border-radius:8px;text-decoration:none">📩 Send Telegram Now</a></p>
    <p style="text-align:center;color:#888;font-size:12px">Auto Telegram every 1 hour | {datetime.now().strftime('%d-%m %H:%M')}</p>
    </body></html>
    """

@app.route("/send_now")
def send_now():
    btc = get_levels("BTC-USD")
    nifty = get_levels("^NSEI")
    msg = f"🔥 <b>NIFTY + BTC UPDATE</b> 🔥\n⏰ {datetime.now().strftime('%d-%m %H:%M')}\n\n"
    if btc:
        msg += f"₿ <b>BTC: ${btc['close']}</b>\n🟢 BUY ABOVE {btc['buy']} | SL {btc['buy_sl']} | TGT {btc['buy_tgt']}\n🔴 SELL BELOW {btc['sell']} | SL {btc['sell_sl']} | TGT {btc['sell_tgt']}\n\n"
    if nifty:
        msg += f"📈 <b>NIFTY: {nifty['close']}</b>\n🟢 BUY ABOVE {nifty['buy']} | SL {nifty['buy_sl']} | TGT {nifty['buy_tgt']}\n🔴 SELL BELOW {nifty['sell']} | SL {nifty['sell_sl']} | TGT {nifty['sell_tgt']}\n"
    send_telegram(msg)
    return f"Sent! Check Telegram<br><br>{msg.replace(chr(10), '<br>')}"

def auto_sender():
    while True:
        time.sleep(3600) # 1 hour ki okasari
        try:
            btc = get_levels("BTC-USD")
            nifty = get_levels("^NSEI")
            if btc or nifty:
                msg = f"⏰ AUTO UPDATE {datetime.now().strftime('%H:%M')}\n\n"
                if btc: msg += f"₿ BTC ${btc['close']} | BUY {btc['buy']} / SELL {btc['sell']}\n"
                if nifty: msg += f"📈 NIFTY {nifty['close']} | BUY {nifty['buy']} / SELL {nifty['sell']}"
                send_telegram(msg)
        except:
            pass

threading.Thread(target=auto_sender, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
