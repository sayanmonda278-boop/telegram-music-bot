import os
import yt_dlp
from collections import defaultdict
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
BOT_TOKEN ="8052637286:AAHkFwnX-Sjepyoos35_6y0pA8izoRZd14g"

music_queues = defaultdict(list)
current_song = {}

# ================= START =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello sir.I am jack sparrow😎😎. Send me a song name or YouTube link!"
    )

# ================= DOWNLOAD / ADD =================

async def download_music(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    chat_id = update.effective_chat.id

    await update.message.reply_text("🔍 Searching...")

    ydl_opts = {
        "format": "bestaudio/best",
        "quiet": True,
        "extract_flat": False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            # Playlist support
            if "list=" in query:
                info = ydl.extract_info(query, download=False)
                for entry in info["entries"]:
                    music_queues[chat_id].append(entry["url"])

                await update.message.reply_text(
                    f"✅ Playlist added! {len(info['entries'])} songs added."
                )

                if len(music_queues[chat_id]) > 0:
                    await play_next(update, context)
                return

            # Normal search
            info = ydl.extract_info(f"ytsearch:{query}", download=False)
            video = info["entries"][0]
            music_queues[chat_id].append(video["webpage_url"])

            await update.message.reply_text(
                f"✅ Added to queue:\n🎵 {video['title']}"
            )

            if len(music_queues[chat_id]) == 1:
                await play_next(update, context)

    except Exception:
        await update.message.reply_text("❌ Error downloading song.")

# ================= PLAY NEXT =================

async def play_next(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if not music_queues[chat_id]:
        return

    url = music_queues[chat_id][0]

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": "song.%(ext)s",
        "quiet": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        title = info["title"]

    current_song[chat_id] = filename

    keyboard = [
        [
            InlineKeyboardButton("⏭ Skip", callback_data="skip"),
            InlineKeyboardButton("⏹ Stop", callback_data="stop"),
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_audio(
        audio=open(filename, "rb"),
        caption=f"🎵 Now Playing:\n{title}",
        reply_markup=reply_markup,
    )

# ================= BUTTON HANDLER =================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    chat_id = query.message.chat.id

    if query.data == "skip":
        if music_queues[chat_id]:
            music_queues[chat_id].pop(0)

        if music_queues[chat_id]:
            await query.edit_message_caption("⏭ Skipping...")
            await play_next(query, context)
        else:
            await query.edit_message_caption("Queue empty.")

    elif query.data == "stop":
        music_queues[chat_id].clear()
        await query.edit_message_caption("⏹ Stopped & queue cleared.")

# ================= QUEUE COMMAND =================

async def show_queue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if not music_queues[chat_id]:
        await update.message.reply_text("🎵 Queue is empty.")
        return

    text = "🎶 Current Queue:\n\n"
    for i, song in enumerate(music_queues[chat_id]):
        text += f"{i+1}. {song}\n"

    await update.message.reply_text(text)

# ================= MAIN =================

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("queue", show_queue))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_music))
app.add_handler(CallbackQueryHandler(button_handler))

print("Bot is running...")
app.run_polling()