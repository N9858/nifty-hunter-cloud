import requests, os
from flask import Flask
import time
app = Flask(__name__)
TOKEN = os.environ.get("TOKEN", "")
CHAT_ID = os.environ.get("CHAT_ID", "")
def send_telegram(msg):
    if not TOKEN or not CHAT_ID: return
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"})
    except: pass
def get_nifty_data():
    try:
        url = "https://query1.finance.yahoo.com/v8/finance/chart/%5ENSEI?interval=1d&range=2d"
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10).json()
        result = r['chart']['result'][0]
        high = result['indicators']['quote'][0]['high'][-2]
        low = result['indicators']['quote'][0]['low'][-2]
        close = result['indicators']['quote'][0]['close'][-2]
        curr = float(result['meta']['regularMarketPrice'])
        return high, low, close, curr
    except Exception as e:
        print(e)
        return None, None, None, None
@app.route('/')
def home():
    high, low, close, curr = get_nifty_data()
    if not high: return "Loading, refresh again"
    buy_level = round(high + 10)
    sell_level = round(low - 10)
    sl_buy = round(buy_level - 40)
    sl_sell = round(sell_level + 40)
    msg = f"<b>NIFTY DAILY ENTRY - {time.strftime('%d-%m-%Y')}</b>\n\nCurrent: {curr}\nY-High: {high} | Y-Low: {low}\n\nBUY: {buy_level} SL: {sl_buy} TGT: {buy_level+80}\nSELL: {sell_level} SL: {sl_sell} TGT: {sell_level-80}"
    send_telegram(msg)
    return msg
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
