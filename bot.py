import requests
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

TOKEN = "8538417344:AAELrbI2KX9JmhHi_EhgCxLXPfPqyl8E29Q"
CHAT_ID = -1003882788938

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

# -----------------------------------
# ดึงชื่อช่องจากหน้าเว็บ
# -----------------------------------
def check_channel(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        res = requests.get(url, headers=headers, timeout=10)

        if res.status_code != 200:
            return None

        # ดึง title จาก HTML
        match = re.search(r"<title>(.*?)</title>", res.text)

        if match:
            title = match.group(1)
            title = title.replace(" - YouTube", "").strip()
            return title

        return "Unknown"

    except:
        return None

# -----------------------------------
# คำสั่ง status
# -----------------------------------
async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_chat.id != CHAT_ID:
        return

    report = "📊 รายงานสถานะช่อง\n\n"

    for url in CHANNEL_URLS:
        name = check_channel(url)

        if name:
            report += f"✅ {name}\n{url}\n\n"
        else:
            report += f"🚨 ไม่พบช่อง\n{url}\n\n"

    await update.message.reply_text(report)

# -----------------------------------
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(
        MessageHandler(filters.TEXT & filters.Regex("^status$", flags=re.IGNORECASE), status_command)
    )

    app.run_polling()

if __name__ == "__main__":
    main()
