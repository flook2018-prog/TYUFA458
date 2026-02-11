import os
import isodate
from urllib.parse import urlparse
import re
from googleapiclient.discovery import build
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# =========================
# CONFIG
# =========================
BOT_TOKEN = os.getenv("BOT_TOKEN")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

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
    "https://www.youtube.com/@คนตื่นบวช1",
    "https://www.youtube.com/@LyricsxThailand7"
]

youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

# =========================
# YOUTUBE SERVICE
# =========================

def get_channel_id_from_url(url: str):
    parsed = urlparse(url)

    if "/channel/" in parsed.path:
        return parsed.path.split("/channel/")[1]

    handle_match = re.search(r"@([^/]+)", parsed.path)
    if handle_match:
        handle = handle_match.group(1)
        res = youtube.search().list(
            part="snippet",
            q=handle,
            type="channel",
            maxResults=1
        ).execute()
        if res["items"]:
            return res["items"][0]["id"]["channelId"]

    return None


def get_uploads_playlist(channel_id):
    res = youtube.channels().list(
        part="contentDetails",
        id=channel_id
    ).execute()

    return res["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]


def get_latest_videos(url, limit=2):
    channel_id = get_channel_id_from_url(url)
    if not channel_id:
        return None

    uploads_id = get_uploads_playlist(channel_id)

    playlist_items = youtube.playlistItems().list(
        part="snippet,contentDetails",
        playlistId=uploads_id,
        maxResults=10
    ).execute()

    video_ids = [
        item["contentDetails"]["videoId"]
        for item in playlist_items["items"]
    ]

    videos = youtube.videos().list(
        part="contentDetails,statistics,snippet",
        id=",".join(video_ids)
    ).execute()

    results = []

    for video in videos["items"]:
        duration = isodate.parse_duration(
            video["contentDetails"]["duration"]
        ).total_seconds()

        if duration >= 60:
            results.append({
                "title": video["snippet"]["title"],
                "published": video["snippet"]["publishedAt"],
                "views": video["statistics"].get("viewCount", 0),
                "likes": video["statistics"].get("likeCount", 0),
                "comments": video["statistics"].get("commentCount", 0)
            })

        if len(results) >= limit:
            break

    return results


# =========================
# TELEGRAM COMMAND
# =========================

async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("กำลังดึงข้อมูล...")

    for url in CHANNELS:
        videos = get_latest_videos(url)

        if not videos:
            await update.message.reply_text(f"❌ ไม่พบข้อมูล {url}")
            continue

        text = f"📺 {url}\n\n"

        for v in videos:
            text += (
                f"📌 {v['title']}\n"
                f"⏰ {v['published']}\n"
                f"👁 {v['views']} | 👍 {v['likes']} | 💬 {v['comments']}\n"
                f"{'-'*30}\n"
            )

        await update.message.reply_text(text)


# =========================
# MAIN
# =========================

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("report", report))

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
