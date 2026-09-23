import os, time, requests, datetime
from dhanhq import DhanContext, dhanhq

CLIENT_ID = os.getenv("1108098176")
ACCESS_TOKEN = os.getenv("user_info = dhan_login.user_profile(access_token)
print(user_info)")
BOT_TOKEN = os.getenv("8891915442:AAHzBqga9LNxc6JG1FytjWnYFXSaCdX60_I")
CHAT_ID = os.getenv("5066142970")

ctx = DhanContext(CLIENT_ID, ACCESS_TOKEN)
dhan = dhanhq(ctx)
last_price = 0

def send_tg(msg):
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                  json={"chat_id": CHAT_ID, "text": msg})

send_tg("🚀 Rao_hunter PERMANENT BOT Started on Cloud!")

while True:
    try:
        now = datetime.datetime.now()
        # Market time only 9:15 to 15:30 IST
        if 9 <= now.hour <= 15:
            ltp = dhan.get_ltp_data(securities={"NSE_INDEX": [13]})
            price = ltp['data']['NSE_INDEX']['13']['last_price']

            if price!= last_price: # price marete ne pampu
                last_price = price
                msg = f"📈 {now.strftime('%H:%M:%S')} NIFTY DHAN LIVE: {price}\nBUY @ {price-20} SL {price-120} TGT {price+100}\nRao_hunter PERMANENT ✅"
                send_tg(msg)
                print(f"Sent {price}")
        time.sleep(60)
    except Exception as e:
        print(e)
        time.sleep(30)
