from flask import Flask
import yfinance as yf
from datetime import datetime

app = Flask(__name__)

def get_levels():
    try:
        ticker = yf.Ticker("^NSEI")
        hist = ticker.history(period="5d", auto_adjust=True)
        if len(hist) < 2:
            return None
        
        # last 2 days
        y_high = float(hist['High'].iloc[-2])
        y_low = float(hist['Low'].iloc[-2])
        curr = float(hist['Close'].iloc[-1])
        
        buy = round(y_high + 10, 0)
        buy_sl = round(buy - 40, 0)
        buy_tgt = round(buy + 80, 0)
        
        sell = round(y_low - 10, 0)
        sell_sl = round(sell + 40, 0)
        sell_tgt = round(sell - 80, 0)
        
        return {
            "date": datetime.now().strftime("%d-%m-%Y"),
            "current": round(curr,1),
            "y_high": y_high,
            "y_low": y_low,
            "buy": buy, "buy_sl": buy_sl, "buy_tgt": buy_tgt,
            "sell": sell, "sell_sl": sell_sl, "sell_tgt": sell_tgt
        }
    except Exception as e:
        print(f"Error: {e}")
        return None

@app.route('/')
def home():
    d = get_levels()
    if not d:
        return "Data loading... wait 10 sec and refresh | Nifty market closed ayithe data raadu, 5 min lo malli chudu"
    
    html = f"""
    <html><head><meta name='viewport' content='width=device-width, initial-scale=1'>
    <style>
    body{{background:#0a0a0a;color:white;font-family:Arial;text-align:center;padding:20px}}
    .card{{background:#1a1a1a;border-radius:20px;padding:20px;margin:15px auto;max-width:400px;box-shadow:0 0 20px #222}}
    .buy{{border-left:5px solid #00ff88}} .sell{{border-left:5px solid #ff4444}}
    h1{{color:#ffd700}} .price{{font-size:28px;font-weight:bold}}
    .level{{font-size:20px;margin:8px}}
    </style></head><body>
    <h1>🎯 NIFTY HUNTER</h1>
    <p>{d['date']} | Current: {d['current']}</p>
    <p>Y-High: {d['y_high']:.1f} | Y-Low: {d['y_low']:.1f}</p>
    
    <div class='card buy'>
        <h2 style='color:#00ff88'>🟢 BUY ABOVE</h2>
        <div class='price'>{d['buy']}</div>
        <div class='level'>SL: {d['buy_sl']} | TGT: {d['buy_tgt']}</div>
    </div>
    
    <div class='card sell'>
        <h2 style='color:#ff4444'>🔴 SELL BELOW</h2>
        <div class='price'>{d['sell']}</div>
        <div class='level'>SL: {d['sell_sl']} | TGT: {d['sell_tgt']}</div>
    </div>
    <p style='color:gray'>Auto updates daily 9:15 AM</p>
    </body></html>
    """
    return html

if __name__ == '__main__':
    app.run()
