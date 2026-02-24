import os
import requests
import pandas as pd
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# =========================
# CONFIG
# =========================
BOT_TOKEN = os.environ.get("BOT_TOKEN")  # set in Cloud Run / Render
TWELVE_API_KEY = "37197ab71cbe450e89e9686c25769470"
CHAT_ID = 595118215

SYMBOLS = {
    "XAUUSD": "XAU/USD",
    "XAGUSD": "XAG/USD",
    "EURUSD": "EUR/USD",
    "AUDUSD": "AUD/USD",
    "EURJPY": "EUR/JPY",
    "US30": "DJI"
}

TIMEFRAME = "5min"
CANDLES = 120

# =========================
# DATA FETCH
# =========================
def fetch_data(symbol):
    url = "https://api.twelvedata.com/time_series"
    params = {
        "symbol": symbol,
        "interval": TIMEFRAME,
        "outputsize": CANDLES,
        "apikey": TWELVE_API_KEY
    }

    r = requests.get(url, params=params, timeout=10)
    data = r.json()

    if "values" not in data:
        return None

    df = pd.DataFrame(data["values"])
    df = df.astype(float)
    df = df.iloc[::-1].reset_index(drop=True)
    return df

# =========================
# SMC / ICT LOGIC
# =========================
def market_structure(df):
    df["swing_high"] = df["high"].rolling(5, center=True).max()
    df["swing_low"] = df["low"].rolling(5, center=True).min()

    last_close = df["close"].iloc[-1]
    prev_swing_high = df["swing_high"].iloc[-6]
    prev_swing_low = df["swing_low"].iloc[-6]

    if last_close > prev_swing_high:
        return "📈 Bullish MSB"
    elif last_close < prev_swing_low:
        return "📉 Bearish MSB"
    else:
        return None

def analyze(symbol):
    df = fetch_data(symbol)
    if df is None or len(df) < 50:
        return None

    msb = market_structure(df)
    if not msb:
        return None

    price = df["close"].iloc[-1]
    return f"{msb}\nPrice: {price:.2f}"

# =========================
# TELEGRAM COMMANDS
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📈 ATLAS FX Online\n"
        "Use /scan to scan the market."
    )

async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    messages = []

    for name, symbol in SYMBOLS.items():
        result = analyze(symbol)
        if result:
            messages.append(f"🔔 {name}\n{result}")

    if messages:
        await update.message.reply_text("\n\n".join(messages))
    else:
        await update.message.reply_text("No valid SMC setups right now.")

# =========================
# AUTO SCAN (OPTIONAL)
# =========================
async def auto_scan(app):
    while True:
        for name, symbol in SYMBOLS.items():
            result = analyze(symbol)
            if result:
                await app.bot.send_message(
                    chat_id=CHAT_ID,
                    text=f"⚡ AUTO SIGNAL\n{name}\n{result}"
                )
        await asyncio.sleep(600)  # every 10 minutes

# =========================
# MAIN
# =========================
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("scan", scan))

    # Uncomment for auto scanning
    # app.job_queue.run_once(lambda _: asyncio.create_task(auto_scan(app)), 1)

    print("ATLAS FX running...")
    app.run_polling()
