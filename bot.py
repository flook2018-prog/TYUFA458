import re
import time
import requests
import asyncio
from telegram import Update, Bot
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    ContextTypes,
    filters,
)

# ====== เปลี่ยนแค่ 3 ค่า นี้ ======
TOKEN = "8538417344:AAELrbI2KX9JmhHi_EhgCxLXPfPqyl8E29Q"
CHAT_ID = -1003882788938
# =================================

CHANNEL_HANDLES = [
    "JOJOCARTOON-p7p",
    "Rasingcartoon",
    "RonaldoNo1-j6j",
    "Iconiccartoon-y5i",
    "ilukpaaaa",
    "Fibzyจะบินบิน",
    "XcghFs",
    "Rolando7k-z9d",
    "ttsundayxremix468",
    "คนตั้นบิน1",
    "LyricsxThailand7"
]

channel_status = {}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/115.0"
}

# ----------------------------
# ดึงข้อมูลหน้า YouTube → เอาชื่อช่อง
# ----------------------------
def fetch_channel_info(handle):
    try:
        url = f"https://www.youtube.com/@{handle}"
        res = requests.get(url, headers=HEADERS, timeout=10)

        if res.status_code != 200:
            return None, None

        html = res.text

        # หา JSON block ที่มีชื่อช่อง
        match = re.search(
            r'{"channelId".+?"title":{"runs":\[\{"text":"([^"]+)"\}\]',
            html
        )

        if match:
            name = match.group(1)
        else:
            name = None

        return "alive", name

    except Exception as e:
        return None, None

# ----------------------------
# เช็คสถานะช่อง
# ----------------------------
async def check_channels(context: ContextTypes.DEFAULT_TYPE):
    global channel_status

    for handle in CHANNEL_HANDLES:
        status, name = fetch_channel_info(handle)

        if status is None:
            status = "dead"

        # ถ้ายังไม่เคยเก็บสถานะ
        if handle not in channel_status:
            channel_status[handle] = status
            continue

        # ถ้าสถานะเปลี่ยน → แจ้งเตือน
        if status != channel_status[handle]:
            if status == "alive":
                msg = f"✅ @{handle} กลับมาออนไลน์"
            else:
                msg = f"🚨 @{handle} หายไปหรือโดนระงับ"
            await context.bot.send_message(chat_id=CHAT_ID, text=msg)
            channel_status[handle] = status

# ----------------------------
# คำสั่ง status ในกลุ่ม
# ----------------------------
async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    report = "📊 รายงานสถานะช่อง YouTube\n\n"

    for handle in CHANNEL_HANDLES:
        status, name = fetch_channel_info(handle)

        if status == "alive" and name:
            report += f"@{handle}\n📌 ชื่อช่อง: {name}\n\n"
        elif status == "alive":
            report += f"@{handle}\n📌 อยู่ แต่หาชื่อไม่เจอ\n\n"
        else:
            report += f"@{handle}\n❌ ไม่พบช่อง / อาจถูกลบ\n\n"

    await update.message.reply_text(report)

# ----------------------------
# เริ่มงานตอนบอทรัน
# ----------------------------
async def on_startup(app):
    await app.bot.send_message(chat_id=CHAT_ID, text="🤖 บอทออนไลน์แล้ว พร้อมเช็คช่อง!")

# ----------------------------
# MAIN
# ----------------------------
def main():
    app = ApplicationBuilder().token(TOKEN).post_init(on_startup).build()

    # รับคำสั่ง / status
    app.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex(r"(?i)^/?status$"),
            status_command,
        )
    )

    # ตรวจทุก 5 นาที
    app.job_queue.run_repeating(check_channels, interval=300, first=10)

    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
