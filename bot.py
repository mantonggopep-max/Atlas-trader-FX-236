import os
import asyncio
from datetime import datetime
import pytz
import MetaTrader5 as mt5  # Make sure MetaTrader5 package is installed
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import pandas as pd

# -----------------------------
# CONFIG / ENVIRONMENT
# -----------------------------
BOT_TOKEN = os.environ.get("BOT_TOKEN")  # Telegram bot token from BotFather
TELEGRAM_CHAT_ID = 595118215  # Mantong's personal chat ID
TIMEZONE = pytz.timezone("Etc/GMT+1")
PAIRS = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD"]
CANDLE_COUNT = 100  # number of candles to analyze for support/resistance

# -----------------------------
# MT5 CONNECTION
# -----------------------------
if not mt5.initialize():
    print("MetaTrader5 initialization failed")
    mt5.shutdown()
    exit()

# -----------------------------
# MARKET DATA FUNCTIONS
# -----------------------------
def fetch_price_data(pair, timeframe=mt5.TIMEFRAME_M5, count=CANDLE_COUNT):
    """Fetch last candles from MT5"""
    rates = mt5.copy_rates_from_pos(pair, timeframe, 0, count)
    if rates is None or len(rates) == 0:
        return None
    df = pd.DataFrame(rates)
    return df

def calculate_support_resistance(df):
    """ICT/SMC-style S/R placeholder"""
    high = df['high'].max()
    low = df['low'].min()
    # Simple pivot levels placeholder
    support = low
    resistance = high
    return support, resistance

def analyze_pair(pair):
    """Check trade opportunity using simple ICT/SMC logic"""
    df = fetch_price_data(pair)
    if df is None:
        return None

    support, resistance = calculate_support_resistance(df)
    last_close = df['close'].iloc[-1]

    # Simple ICT/SMC logic (breakout/breakdown)
    if last_close > resistance:
        return f"{pair} 📈 Bullish breakout above {resistance:.5f}"
    elif last_close < support:
        return f"{pair} 📉 Bearish breakdown below {support:.5f}"
    else:
        return None

# -----------------------------
# NEWS FILTER
# -----------------------------
def fetch_news():
    """Placeholder for news integration (ForexFactory/TradingEconomics)"""
    return ["No high-impact news currently"]

# -----------------------------
# TELEGRAM HANDLERS
# -----------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📈 ATLAS FX Trading Bot Online!\n"
        "Commands:\n"
        "/scan - Scan major pairs\n"
        "/news - Latest news"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start - Initialize bot\n"
        "/scan - Scan all major pairs\n"
        "/news - Latest high-impact news\n"
    )

async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    signals = []
    for pair in PAIRS:
        signal = analyze_pair(pair)
        if signal:
            signals.append(signal)
    if signals:
        await update.message.reply_text("\n".join(signals))
    else:
        await update.message.reply_text("No trade opportunities detected now.")

async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    latest_news = fetch_news()
    await update.message.reply_text("\n".join(latest_news))

# -----------------------------
# AUTO SIGNAL FUNCTION
# -----------------------------
async def auto_scan():
    while True:
        signals = []
        for pair in PAIRS:
            signal = analyze_pair(pair)
            if signal:
                signals.append(signal)
        if signals:
            for s in signals:
                await app.bot.send_message(TELEGRAM_CHAT_ID, f"🟢 Auto Signal: {s}")
        await asyncio.sleep(300)  # scan every 5 minutes

# -----------------------------
# BOT APPLICATION
# -----------------------------
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("scan", scan))
app.add_handler(CommandHandler("news", news))

# -----------------------------
# START BOT
# -----------------------------
if __name__ == "__main__":
    asyncio.create_task(auto_scan())  # enable background auto scan
    print("ATLAS FX Bot started...")
    app.run_polling()
