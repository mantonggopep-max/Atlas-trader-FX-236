from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os

# Load token from environment variable
BOT_TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ATLAS FX online.\nUse /scan to analyze the market.\nSignals will arrive here on your phone."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Available commands:\n"
        "/start - Initialize bot\n"
        "/scan - Scan all major pairs\n"
        "/pair [PAIR] - Analyze a specific pair\n"
        "/news - Today's high-impact news\n"
        "/risk - Current risk-on / risk-off status\n"
        "/sessions - Active session info"
    )

# Build bot application
app = ApplicationBuilder().token(BOT_TOKEN).build()

# Add command handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))

# Start bot
app.run_polling()
