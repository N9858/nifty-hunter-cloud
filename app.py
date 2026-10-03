import os, time, requests
from datetime import datetime

BOT_TOKEN = os.getenv("8802132310:AAFWkkr9V06Yq-B4hiB6QTG--2JBpgXVE14")
CHAT_ID = os.getenv("5066142970")

last_trend = ""

def send(text):
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": text}, timeout=10)
    except:
        pass

print("BOT STARTED - CLEAN NO SPAM")

while True:
    try:
        r = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT", timeout=10).json()
        price = float(r['price'])
    except:
        price = 84500.0

    now = datetime.now().strftime("%I:%M %p IST - %d %b")
    
    if price < 83726:
        trend = "BEARISH"
        setup = f"SELL BREAKDOWN CONFIRMED\nSell Below: 83726\nTarget: 82876\nSL: 85417"
        status = "SELL NOW - Breakdown Done"
        icon = "📉 DOWN"
    elif price > 85416:
        trend = "BULLISH"
        setup = f"BUY BREAKOUT CONFIRMED\nBuy Above: 85416\nTarget: 86266\nSL: 83724"
        status = "BUY NOW - Breakout Done"
        icon = "📈 UP"
    else:
        trend = "SIDEWAYS"
        setup = f"NO TRADE ZONE\nRange: 83726 - 85416"
        status = "WAIT FOR BREAKOUT - Ippudu entry vaddu"
        icon = "SIDEWAYS"

    if trend != last_trend:
        msg = f"BTC PRO BOT - LIVE\nTime: {now}\nPrice: ${price} {icon}\nTrend: {trend}\n\n{setup}\nStatus: {status}"
        send(msg)
        last_trend = trend
        print(f"SENT {trend}")
    else:
        print(f"SKIP {trend}")

    time.sleep(1800)
