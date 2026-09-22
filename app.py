from flask import Flask, request
import yfinance as yf
import requests
from datetime import datetime

app = Flask(__name__)

# --- FINAL TOKENS ---
BOT_TOKEN = "8960559093:AAEcfT8WxfbH9sfGdB1t7vdrDmCsVe85fH8"
CHAT_ID = "5066142970"

def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
        r = requests.post(url, data=data, timeout=10)
        return r.text
    except Exception as e:
        return str(e)

def get_levels(symbol):
    try:
        data = yf.download(symbol, period="2d", interval="1d")
        last = data.iloc[-1]
        close = float(last['Close'])
        high = float(last['High'])
        low = float(last['Low'])
        
        # Simple Hunter Logic
        buy_level = round(high + (high-low)*0.2, 2)
        buy_sl = round(buy_level - (high-low)*0.3, 2)
        buy_tgt = round(buy_level + (high-low)*0.5, 2)
        
        sell_level = round(low - (high-low)*0.2, 2)
        sell_sl = round(sell_level + (high-low)*0.3, 2)
        sell_tgt = round(sell_level - (high-low)*0.5, 2)
        
        return close, buy_level, buy_sl, buy_tgt, sell_level, sell_sl, sell_tgt
    except:
        return 0,0,0,0,0,0,0

@app.route("/")
def home():
    btc_close, btc_buy, btc_bsl, btc_btgt, btc_sell, btc_ssl, btc_stgt = get_levels("BTC-USD")
    nifty_close, n_buy, n_bsl, n_btgt, n_sell, n_ssl, n_stgt = get_levels("^NSEI")

    html = f"""
    <body style="background:black;color:white;font-family:Arial;padding:20px">
    <h2 style="text-align:center">🔥 NIFTY + BTC HUNTER 🔥</h2>
    
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
    <a href="/send_now" style="background:#0a4a6b;color:white;padding:10px 20px;text-decoration:none;border-radius:8px">📩 Send Telegram Now</a>
    <p style="font-size:12px;color:gray">{datetime.now()}</p>
    </div>
    </body>
    """
    return html

@app.route("/send_now")
def send_now():
    btc_close, btc_buy, btc_bsl, btc_btgt, btc_sell, btc_ssl, btc_stgt = get_levels("BTC-USD")
    nifty_close, n_buy, n_bsl, n_btgt, n_sell, n_ssl, n_stgt = get_levels("^NSEI")
    
    msg = f"🔥 *NIFTY + BTC HUNTER* 🔥\n\n₿ *BTC: {btc_close}*\nBUY ABOVE {btc_buy} | SL {btc_bsl} | TGT {btc_btgt}\nSELL BELOW {btc_sell} | SL {btc_ssl} | TGT {btc_stgt}\n\n📈 *NIFTY: {nifty_close}*\nBUY ABOVE {n_buy} | SL {n_bsl} | TGT {n_btgt}\nSELL BELOW {n_sell} | SL {n_ssl} | TGT {n_stgt}"
    
    result = send_telegram(msg)
    return f"<h3>Telegram Result:</h3><pre>{result}</pre><br><a href='/'>Go Back</a><p>If 'ok':true vasthe Telegram vachindi!</p>"

@app.route("/check_bot")
def check_bot():
    r = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getMe")
    return f"<pre>{r.text}</pre>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
