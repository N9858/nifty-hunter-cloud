import os, time, requests, threading
from datetime import datetime
import pytz
from flask import Flask

# --- RENDER PORT FIX ---
app = Flask(__name__)
@app.route('/')
def home(): return "NIFTY 50 ULTIMATE LIVE"
def run_web(): app.run(host='0.0.0.0', port=10000)
threading.Thread(target=run_web, daemon=True).start()
# -----------------------

BOT_TOKEN = os.getenv("8742634693:AAFg-Kj8kb3COA1Dv-FqXSvOlyD75zt3mzc")
CHAT_ID = os.getenv("5066142970")
IST = pytz.timezone('Asia/Kolkata')
last_trend = "SIDEWAYS"

def send(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except: pass

def get_nifty_live():
    try:
        # LIVE NIFTY from Yahoo - 15m candles
        url = "https://query1.finance.yahoo.com/v8/finance/chart/%5ENSEI?interval=15m&range=5d"
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10).json()
        closes = r['chart']['result'][0]['indicators']['quote'][0]['close']
        volumes = r['chart']['result'][0]['indicators']['quote'][0]['volume']
        closes = [c for c in closes if c is not None][-100:]
        volumes = [v for v in volumes if v is not None][-100:]

        def ema(data, p):
            k = 2/(p+1)
            e = data[0]
            for v in data[1:]: e = v*k + e*(1-k)
            return e

        ema9 = ema(closes, 9)
        ema21 = ema(closes, 21)
        ema50 = ema(closes, 50)

        # RSI
        gains, losses = [], []
        for i in range(1, 15):
            d = closes[-i] - closes[-i-1]
            (gains if d>0 else losses).append(abs(d))
        ag = sum(gains)/14 if gains else 0
        al = sum(losses)/14 if losses else 0.01
        rsi = 100 - (100/(1+ag/al))

        # MACD
        ema12 = ema(closes[-26:], 12)
        ema26 = ema(closes[-26:], 26)
        macd = ema12 - ema26
        macd_list = [ema(closes[-34+j:-8+j], 12) - ema(closes[-34+j:-8+j], 26) for j in range(9)]
        signal = ema(macd_list, 9)
        macd_bull = macd > signal

        # Volume Spike
        avg_vol = sum(volumes[-20:])/20
        vol_spike = volumes[-1] > avg_vol*1.2

        # AUTO Support Resistance - Last 20 High Low
        last20 = closes[-20:]
        SUP = min(last20)
        RES = max(last20)

        return closes[-1], ema9, ema21, ema50, rsi, macd, signal, macd_bull, vol_spike, SUP, RES
    except Exception as e:
        print("Nifty Error", e)
        return None

print("NIFTY 50 ULTIMATE LIVE STARTED")

while True:
    now = datetime.now(IST)
    # Market Hours: Mon-Fri 9:15 to 15:30
    if now.weekday() >= 5 or not (9 <= now.hour < 16):
        print(f"MARKET CLOSED {now.strftime('%H:%M')}")
        time.sleep(180)
        continue

    data = get_nifty_live()
    if not data:
        time.sleep(30)
        continue

    price, ema9, ema21, ema50, rsi, macd, signal, macd_bull, vol_spike, SUPPORT, RESISTANCE = data
    RANGE = RESISTANCE - SUPPORT
    if RANGE < 30: RANGE = 80
    t_str = now.strftime("%I:%M %p - %d %b")

    if price < SUPPORT: trend = "BEARISH"
    elif price > RESISTANCE: trend = "BULLISH"
    else: trend = "SIDEWAYS"

    if trend!= last_trend and trend!= "SIDEWAYS":
        fake = False
        if trend == "BULLISH":
            if not (ema9 > ema21 and price > ema50 and 45 < rsi < 75 and macd_bull): fake = True
            if fake:
                print(f"FAKE BUY IGNORE RSI:{rsi:.1f}")
                last_trend = trend
                time.sleep(60)
                continue
            t1 = RESISTANCE + RANGE*0.618
            t2 = RESISTANCE + RANGE*1.0
            t3 = RESISTANCE + RANGE*1.618
            t4 = RESISTANCE + RANGE*2.618
            msg = f"""🚀 NIFTY 50 BREAKOUT - BUY ✅ LIVE

Time: {t_str}
Price: {price:.2f} 📈 REAL BULLISH

📊 CONFIRMED:
RSI: {rsi:.1f} ✅ | EMA9 {ema9:.0f} > EMA21 {ema21:.0f} ✅
Price > EMA50 {ema50:.0f} ✅
MACD: {macd:.2f} > {signal:.2f} ✅ {"🔥 VOL SPIKE" if vol_spike else ""}

📐 FIB TARGETS:
Entry > {RESISTANCE:.0f}
T1 {t1:.0f} (0.618) | T2 {t2:.0f} (1.0)
T3 {t3:.0f} (1.618) | T4 {t4:.0f} (2.618)
🛑 SL: {SUPPORT:.0f}"""
            send(msg)

        else: # BEARISH
            if not (ema9 < ema21 and price < ema50 and 25 < rsi < 55 and not macd_bull): fake = True
            if fake:
                print(f"FAKE SELL IGNORE RSI:{rsi:.1f}")
                last_trend = trend
                time.sleep(60)
                continue
            t1 = SUPPORT - RANGE*0.618
            t2 = SUPPORT - RANGE*1.0
            t3 = SUPPORT - RANGE*1.618
            t4 = SUPPORT - RANGE*2.618
            msg = f"""🔻 NIFTY 50 BREAKDOWN - SELL ✅ LIVE

Time: {t_str}
Price: {price:.2f} 📉 REAL BEARISH

RSI: {rsi:.1f} ✅ | EMA9 < EMA21 ✅
Price < EMA50 ✅ | MACD Bear ✅

🎯 FIB TARGETS:
Entry < {SUPPORT:.0f}
T1 {t1:.0f} | T2 {t2:.0f}
T3 {t3:.0f} | T4 {t4:.0f}
🛑 SL: {RESISTANCE:.0f}"""
            send(msg)
        last_trend = trend
        print(f"SENT NIFTY {trend}")

    else:
        print(f"WAIT {trend} P:{price:.0f} RSI:{rsi:.1f} S:{SUPPORT:.0f} R:{RESISTANCE:.0f}")

    time.sleep(60)
