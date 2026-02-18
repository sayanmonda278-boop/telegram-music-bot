import os
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = "8052637286:AAHkFwnX-Sjepyoos35_6y0pA8izoRZd14g"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello sir.I am jack sparrow😎😎.Send me a song name and I will send you the music!🎶🎶")

async def download_music(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    await update.message.reply_text("🔍 Searching...")

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'song.%(ext)s',
        'quiet': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{query}", download=True)
            video = info['entries'][0]
            filename = ydl.prepare_filename(video)

        await update.message.reply_audio(audio=open(filename, 'rb'))
        os.remove(filename)

    except Exception as e:
        await update.message.reply_text("❌ Error downloading song.")

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_music))

print("Bot is running...")
app.run_polling()
