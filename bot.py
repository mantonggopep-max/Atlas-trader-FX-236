import os
import requests
import pandas as pd
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# =========================
# CONFIG
# =========================
BOT_TOKEN = os.environ["BOT_TOKEN"]
TWELVE_API_KEY = os.environ["TWELVE_API_KEY"]

SYMBOLS = {
    "XAUUSD": "XAU/USD",
    "XAGUSD": "XAG/USD",
    "EURUSD": "EUR/USD",
    "AUDUSD": "AUD/USD",
    "EURJPY": "EUR/JPY",
    "US30": "DJI"
}

TIMEFRAME = "5min"
CANDLES = 100

# =========================
# DATA FETCH
# =========================
def fetch_data(symbol):
    url = "https://api.twelvedata.com/time_series"
    params = {
        "symbol": SYMBOLS[symbol],
        "interval": TIMEFRAME,
        "outputsize": CANDLES,
        "apikey": TWELVE_API_KEY
    }

    r = requests.get(url, params=params, timeout=10)
    data = r.json()

    if "values" not in data:
        return None

    df = pd.DataFrame(data["values"])

    price_cols = ["open", "high", "low", "close"]
    df[price_cols] = df[price_cols].astype(float)
    df["datetime"] = pd.to_datetime(df["datetime"])

    df = df.sort_values("datetime").reset_index(drop=True)
    return df

# =========================
# ICT / SMC ANALYSIS
# =========================
def analyze(symbol):
    df = fetch_data(symbol)
    if df is None or len(df) < 20:
        return None

    last = df.iloc[-1]
    prev = df.iloc[-2]

    signals = []

    # Market Structure Break (simple & clean)
    if last["close"] > prev["high"]:
        signals.append(f"📈 {symbol} Bullish MSB\nEntry above {prev['high']:.2f}")
    elif last["close"] < prev["low"]:
        signals.append(f"📉 {symbol} Bearish MSB\nEntry below {prev['low']:.2f}")

    return "\n".join(signals) if signals else None

# =========================
# TELEGRAM COMMANDS
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📈 ATLAS FX Online\n"
        "Pairs: XAUUSD, XAGUSD, EURUSD, AUDUSD, EURJPY, US30\n"
        "Use /scan to check market structure."
    )

async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    messages = []

    for symbol in SYMBOLS:
        result = analyze(symbol)
        if result:
            messages.append(result)

    if messages:
        await update.message.reply_text("\n\n".join(messages))
    else:
        await update.message.reply_text("No valid ICT structure at the moment.")

# =========================
# MAIN
# =========================
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("scan", scan))

    print("ATLAS FX Bot running...")
    app.run_polling()
