import requests
import re
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

# ====== ใส่ค่าของคุณ ======
TOKEN = "8538417344:AAELrbI2KX9JmhHi_EhgCxLXPfPqyl8E29Q"
CHAT_ID = -1003882788938
# ===========================

CHANNEL_URLS = [
    "https://www.youtube.com/@JOJOCARTOON-p7p",
    "https://www.youtube.com/@Rasingcartoon",
    "https://www.youtube.com/@RonaldoNo1-j6j",
    "https://www.youtube.com/@Iconiccartoon-y5i",
    "https://www.youtube.com/@ilukpaaaa",
    "https://www.youtube.com/@Fibzy%E0%B8%88%E0%B8%B0%E0%B9%82%E0%B8%9A%E0%B8%99%E0%B8%9A%E0%B8%B4%E0%B8%99",
    "https://www.youtube.com/@XcghFs",
    "https://www.youtube.com/@Rolando7k-z9d",
    "https://www.youtube.com/@ttsundayxremix468",
    "https://www.youtube.com/@%E0%B8%84%E0%B8%99%E0%B8%95%E0%B8%B7%E0%B9%88%E0%B8%99%E0%B8%9A%E0%B8%B21",
    "https://www.youtube.com/@LyricsxThailand7"
]

channel_status = {}

# -----------------------------
# ดึงชื่อช่องจากหน้าเว็บ
# -----------------------------
def get_channel_name(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        res = requests.get(url, headers=headers, timeout=10)

        if res.status_code != 200:
            return None

        soup = BeautifulSoup(res.text, "html.parser")

        meta = soup.find("meta", property="og:title")
        if meta:
            return meta["content"]

        return None

    except:
        return None


# -----------------------------
# เช็คทุกช่อง
# -----------------------------
async def check_channels(context: ContextTypes.DEFAULT_TYPE):
    global channel_status

    for url in CHANNEL_URLS:
        name = get_channel_name(url)
        status = "alive" if name else "dead"

        if url not in channel_status:
            channel_status[url] = status
            continue

        if status != channel_status[url]:
            if status == "alive":
                message = f"✅ {name} กลับมาแล้ว"
            else:
                message = f"🚨 {url} เข้าไม่ได้แล้ว"

            await context.bot.send_message(chat_id=CHAT_ID, text=message)
            channel_status[url] = status


# -----------------------------
# คำสั่ง status
# -----------------------------
async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != CHAT_ID:
        return

    report = "📊 รายงานสถานะช่อง\n\n"

    for url in CHANNEL_URLS:
        name = get_channel_name(url)
        if name:
            report += f"{name}\nStatus: ✅ Alive\n\n"
        else:
            report += f"{url}\nStatus: 🚨 Not Found\n\n"

    await update.message.reply_text(report)


# -----------------------------
# เริ่มระบบ
# -----------------------------
async def on_startup(app):
    await app.bot.send_message(chat_id=CHAT_ID, text="🤖 บอทเฝ้าช่องออนไลน์แล้ว")


def main():
    app = ApplicationBuilder().token(TOKEN).post_init(on_startup).build()

    app.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex("(?i)^/?status$"),
            status_command
        )
    )

    app.job_queue.run_repeating(check_channels, interval=300, first=10)

    app.run_polling()


if __name__ == "__main__":
    main()
