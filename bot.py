import requests
import asyncio
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

# ====== ใส่ค่าของคุณ ======
TOKEN = "8538417344:AAELrbI2KX9JmhHi_EhgCxLXPfPqyl8E29Q"
CHAT_ID = -1003882788938   # ใส่เป็นตัวเลข ไม่ต้องใส่ ""
API_KEY = "AIzaSyB6wTJ74st9Q-MGWYFpNATxZ3ghHbgokpM"
# ===========================

CHANNEL_HANDLES = [
    "JOJOCARTOON-p7p",
    "Rasingcartoon",
    "RonaldoNo1-j6j",
    "Iconiccartoon-y5i"
]

channel_status = {}

# -----------------------------
# ดึง Channel ID
# -----------------------------
def get_channel_id(handle):
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": handle,
        "type": "channel",
        "key": API_KEY
    }

    res = requests.get(url, params=params).json()

    if "items" in res and len(res["items"]) > 0:
        return res["items"][0]["snippet"]["channelId"]

    return None

# -----------------------------
# เช็คสถานะทุกช่อง
# -----------------------------
async def check_channels(context: ContextTypes.DEFAULT_TYPE):
    global channel_status

    for handle in CHANNEL_HANDLES:
        channel_id = get_channel_id(handle)
        status = "alive" if channel_id else "dead"

        if handle not in channel_status:
            channel_status[handle] = status
            continue

        if status != channel_status[handle]:
            if status == "alive":
                message = f"✅ {handle} กลับมาแล้ว"
            else:
                message = f"🚨 {handle} อาจโดนระงับ / ค้นหาไม่พบ"

            await context.bot.send_message(chat_id=CHAT_ID, text=message)
            channel_status[handle] = status

# -----------------------------
# คำสั่ง status
# -----------------------------
async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != CHAT_ID:
        return

    report = "📊 รายงานสถานะช่อง\n\n"

    for handle in CHANNEL_HANDLES:
        channel_id = get_channel_id(handle)
        status = "✅ Alive" if channel_id else "🚨 Not Found"
        report += f"{handle}\nStatus: {status}\n\n"

    await update.message.reply_text(report)

# -----------------------------
# เริ่มต้นระบบ
# -----------------------------
async def on_startup(app):
    await app.bot.send_message(chat_id=CHAT_ID, text="🤖 บอทเฝ้าช่องออนไลน์แล้ว")

# -----------------------------
# main
# -----------------------------
def main():
    app = ApplicationBuilder().token(TOKEN).post_init(on_startup).build()

    # รับข้อความคำว่า status
    app.add_handler(
        MessageHandler(filters.TEXT & filters.Regex("^(?i)status$"), status_command)
    )

    # ตั้ง job เช็คทุก 5 นาที
    job_queue = app.job_queue
    job_queue.run_repeating(check_channels, interval=300, first=10)

    app.run_polling()

if __name__ == "__main__":
    main()
