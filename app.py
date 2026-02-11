import requests
import re
from bs4 import BeautifulSoup
from telegram.ext import Updater, CommandHandler

TOKEN = "8538417344:AAELrbI2KX9JmhHi_EhgCxLXPfPqyl8E29Q"

CHANNELS = [
    "https://www.youtube.com/@JOJOCARTOON-p7p",
    "https://www.youtube.com/@Rasingcartoon",
    "https://www.youtube.com/@RonaldoNo1-j6j",
    "https://www.youtube.com/@Iconiccartoon-y5i",
    "https://www.youtube.com/@ilukpaaaa",
    "https://www.youtube.com/@Fibzyจะโบนบิน",
    "https://www.youtube.com/@XcghFs",
    "https://www.youtube.com/@Rolando7k-z9d",
    "https://www.youtube.com/@ttsundayxremix468",
    "https://www.youtube.com/@คนตื่นบา1",
    "https://www.youtube.com/@LyricsxThailand7"
]

def fetch_latest_video(channel_url):
    headers = {"User-Agent": "Mozilla/5.0"}

    r = requests.get(channel_url + "/videos", headers=headers)

    if r.status_code == 404 or "terminated" in r.text.lower():
        return {"status": "TERMINATED"}

    soup = BeautifulSoup(r.text, "html.parser")

    # ดึง video id ตัวแรกที่ไม่ใช่ shorts
    match = re.search(r'"videoId":"(.*?)"', r.text)
    if not match:
        return {"status": "ACTIVE", "video": "ไม่พบวิดีโอ"}

    video_id = match.group(1)
    video_url = f"https://www.youtube.com/watch?v={video_id}"

    vr = requests.get(video_url, headers=headers)
    video_html = vr.text

    view_match = re.search(r'"viewCount":"(.*?)"', video_html)
    like_match = re.search(r'"label":"([\d,]+) likes"', video_html)
    comment_match = re.search(r'"countText":\{"simpleText":"([\d,]+) Comments"', video_html)

    return {
        "status": "ACTIVE",
        "views": view_match.group(1) if view_match else "N/A",
        "likes": like_match.group(1) if like_match else "N/A",
        "comments": comment_match.group(1) if comment_match else "N/A",
    }

def check(update, context):
    for url in CHANNELS:
        data = fetch_latest_video(url)

        if data["status"] == "TERMINATED":
            msg = f"❌ {url}\nSTATUS: TERMINATED\n"
        else:
            msg = (
                f"✅ {url}\n"
                f"STATUS: ACTIVE\n"
                f"Views: {data['views']}\n"
                f"Likes: {data['likes']}\n"
                f"Comments: {data['comments']}\n"
            )

        update.message.reply_text(msg)

def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("check", check))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
