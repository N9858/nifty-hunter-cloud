import os, requests, time

# Render lo Environment Variable nundi token teeskuntadi - Safe!
TOKEN = os.getenv("8742634693:AAFg-Kj8kb3COA1Dv-FqXSvOlyD75zt3mzc")
CHAT_ID = os.getenv("5066142970")

def send_telegram(msg):
    if not TOKEN or not CHAT_ID:
        print("Token/Chat ID missing in Env Vars!")
        return
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.get(url, params={"chat_id": CHAT_ID, "text": msg}, timeout=10)
        print(f"✅ Telegram Sent: {msg}")
    except Exception as e:
        print(f"Telegram Error: {e}")

print("🚀 LIVE NIFTY BOT + TELEGRAM 24/7 STARTED...")
send_telegram("✅ Nifty Hunter Cloud Bot Started! 24/7 LIVE")

BUY_LEVEL = 22480
SELL_LEVEL = 22380
NO_LOW, NO_HIGH = 22400, 22450

while True:
    try:
        r = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/%5ENSEI", headers={"User-Agent":"Mozilla/5.0"}, timeout=10).json()
        price = r['chart']['result'][0]['meta']['regularMarketPrice']
        now = time.strftime('%H:%M:%S')
        print(f"LIVE NIFTY: {price} | {now}")

        if NO_LOW < price < NO_HIGH:
            print(f"--> NO TRADE ZONE {NO_LOW}-{NO_HIGH}")
        elif price >= BUY_LEVEL:
            msg = f"🟢 BUY BREAKOUT! Nifty {price} -> Targets: 22520 / 22580"
            print(msg)
            send_telegram(msg)
            time.sleep(300)
        elif price <= SELL_LEVEL:
            msg = f"🔴 SELL BREAKDOWN! Nifty {price} -> Targets: 22330 / 22280"
            print(msg)
            send_telegram(msg)
            time.sleep(300)
        else:
            print("--> Waiting for level...")
        time.sleep(60)
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(60)
        
