import os, asyncio, logging, yfinance as yf
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("8949955888:AAFFQs2DgleYMBqveDXehyefspqu4Q12DsQ")
CHAT_ID = os.getenv("5066142970")

logging.basicConfig(level=logging.INFO)

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = """
🔥 **Swing Hunter Bot LIVE!** 🔥

✅ Deploy Success!

Commands:
• /start - Bot status
• /nifty - Nifty 50 live price
• /sensex - Sensex live price
• /hunt - Top swing picks

Bot 24/7 Cloud lo run avuthondi!
    """
    await update.message.reply_text(msg, parse_mode='Markdown')

# /nifty command
async def nifty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = yf.Ticker("^NSEI").history(period="1d")
        price = data['Close'].iloc[-1]
        await update.message.reply_text(f"📈 NIFTY 50: {price:.2f}")
    except:
        await update.message.reply_text("Nifty data loading... try again")

# /sensex command
async def sensex(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = yf.Ticker("^B
