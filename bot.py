import os
import requests
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

CHANNELS = {
    "JOJOCARTOON": "JOJOCARTOON-p7p",
    "Rasingcartoon": "Rasingcartoon",
    "RonaldoNo1": "RonaldoNo1-j6j",
    "Iconiccartoon": "Iconiccartoon-y5i",
    "ilukpaaaa": "ilukpaaaa",
    "Fibzy": "Fibzyจะโบนบิน",
    "XcghFs": "XcghFs",
    "Rolando7k": "Rolando7k-z9d",
    "ttsundayxremix": "ttsundayxremix468",
    "คนตื่นบ้า": "คนตื่นบ้า1",
    "LyricsxThailand": "LyricsxThailand7"
}


# =========================
# 🔍 Helper Functions
# =========================

def get_channel_id_from_handle(handle):
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&type=channel&q={handle}&key={YOUTUBE_API_KEY}"
    r = requests.get(url).json()
    return r["items"][0]["snippet"]["channelId"]


def get_channel_info(channel_id):
    url = f"https://www.googleapis.com/youtube/v3/channels?part=snippet,statistics,contentDetails&id={channel_id}&key={YOUTUBE_API_KEY}"
    r = requests.get(url).json()
    return r["items"][0]


def get_latest_videos(playlist_id):
    url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&maxResults=2&playlistId={playlist_id}&key={YOUTUBE_API_KEY}"
    r = requests.get(url).json()
    return r["items"]


def get_video_stats(video_ids):
    ids = ",".join(video_ids)
    url = f"https://www.googleapis.com/youtube/v3/videos?part=statistics&id={ids}&key={YOUTUBE_API_KEY}"
    r = requests.get(url).json()
    return {item["id"]: item["statistics"] for item in r["items"]}


# =========================
# 📩 Telegram Command
# =========================

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = "📊 YouTube Channel Report\n"

    for name, handle in CHANNELS.items():
        try:
            channel_id = get_channel_id_from_handle(handle)
            channel_data = get_channel_info(channel_id)

            title = channel_data["snippet"]["title"]
            subs = channel_data["statistics"].get("subscriberCount", "0")
            total_videos = channel_data["statistics"].get("videoCount", "0")

            uploads_playlist = channel_data["contentDetails"]["relatedPlaylists"]["uploads"]
            latest_videos = get_latest_videos(uploads_playlist)

            video_ids = [v["snippet"]["resourceId"]["videoId"] for v in latest_videos]
            stats_map = get_video_stats(video_ids)

            message += f"\n\n📺 {title}"
            message += f"\n👥 Subscribers: {subs}"
            message += f"\n🎬 Total Videos: {total_videos}\n"

            for v in latest_videos:
                vid = v["snippet"]["resourceId"]["videoId"]
                video_title = v["snippet"]["title"]
                published = v["snippet"]["publishedAt"]
                stats = stats_map.get(vid, {})

                message += (
                    f"\n🎥 {video_title}"
                    f"\n🕒 {published}"
                    f"\n👁 {stats.get('viewCount', '0')}"
                    f"\n👍 {stats.get('likeCount', '0')}"
                    f"\n💬 {stats.get('commentCount', '0')}\n"
                )

        except Exception as e:
            message += f"\n❌ {name} error: {str(e)}\n"

    await update.message.reply_text(message[:4000])


# =========================
# 🚀 Main
# =========================

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex("(?i)^status$"),
            status_command
        )
    )

    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
