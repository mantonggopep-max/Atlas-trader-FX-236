import os
import asyncio
import pytz
import MetaTrader5 as mt5
import pandas as pd
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# --- CONFIG ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
TELEGRAM_CHAT_ID = int(os.environ.get("TELEGRAM_CHAT_ID", "595118215"))
INSTRUMENTS = ["XAUUSD", "EURUSD", "AUDUSD", "EURJPY", "XAGUSD", "US30"]
SCAN_INTERVAL = 300  # 5 minutes

# --- MT5 INIT ---
def start_mt5():
    if not mt5.initialize():
        print("MT5 Initialization Failed")
        return False
    return True

# --- SMC / ICT LOGIC ---
def analyze_instrument(symbol):
    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, 100)
    if rates is None or len(rates) == 0:
        return None
    
    df = pd.DataFrame(rates)
    last_close = df['close'].iloc[-1]
    prev_high = df['high'].iloc[-2]
    prev_low = df['low'].iloc[-2]

    signals = []
    if last_close > prev_high:
        signals.append(f"📈 {symbol} MSB Bullish")
    elif last_close < prev_low:
        signals.append(f"📉 {symbol} MSB Bearish")
    return signals

# --- TELEGRAM HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📈 ATLAS FX Bot Online!\nUse /scan to scan instruments."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("/start - Bot info\n/scan - Scan instruments")

async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    all_signals = []
    for symbol in INSTRUMENTS:
        sigs = analyze_instrument(symbol)
        if sigs:
            all_signals.extend(sigs)
    if all_signals:
        await update.message.reply_text("\n".join(all_signals))
    else:
        await update.message.reply_text("No trade opportunities detected now.")

# --- AUTO SCAN ---
async def auto_scan(app):
    while True:
        all_signals = []
        for symbol in INSTRUMENTS:
            sigs = analyze_instrument(symbol)
            if sigs:
                all_signals.extend(sigs)
        if all_signals:
            for s in all_signals:
                await app.bot.send_message(TELEGRAM_CHAT_ID, f"🟢 Auto Signal: {s}")
        await asyncio.sleep(SCAN_INTERVAL)

# --- MAIN ---
if __name__ == "__main__":
    if start_mt5():
        app = ApplicationBuilder().token(BOT_TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("help", help_command))
        app.add_handler(CommandHandler("scan", scan))

        # Start auto scan in background
        asyncio.create_task(auto_scan(app))

        print("ATLAS FX Bot running...")
        app.run_polling()
