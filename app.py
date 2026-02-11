import requests
import re
import time
from bs4 import BeautifulSoup
from database import init_db, get_channel, update_channel
from telegram_alert import send_alert

CHECK_INTERVAL = 300  # 5 นาที

def fetch_channel(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        r = requests.get(url + "/videos", headers=headers, timeout=15)

        if r.status_code == 404:
            return {"status": "TERMINATED"}

        if "This account has been terminated" in r.text:
            return {"status": "TERMINATED"}

        text = r.text

        sub_match = re.search(r'"subscriberCountText".*?"simpleText":"(.*?)"', text)
        subscribers = sub_match.group(1) if sub_match else "N/A"

        view_match = re.search(r'"viewCountText".*?"simpleText":"(.*?)"', text)
        views = view_match.group(1) if view_match else "N/A"

        video_match = re.search(r'"videosCountText".*?"simpleText":"(.*?)"', text)
        videos = video_match.group(1) if video_match else "N/A"

        return {
            "status": "ACTIVE",
            "subscribers": subscribers,
            "views": views,
            "videos": videos
        }

    except:
        return {"status": "ERROR"}

def monitor():
    init_db()

    with open("channels.txt") as f:
        channels = [line.strip() for line in f.readlines()]

    while True:
        for url in channels:
            new_data = fetch_channel(url)
            old_data = get_channel(url)

            if not old_data:
                update_channel(
                    url,
                    new_data.get("status"),
                    new_data.get("subscribers"),
                    new_data.get("views"),
                    new_data.get("videos"),
                )
                continue

            old_status = old_data[1]
            new_status = new_data.get("status")

            if old_status != new_status:
                send_alert(f"🚨 STATUS CHANGED\n{url}\n{old_status} ➜ {new_status}")

            update_channel(
                url,
                new_status,
                new_data.get("subscribers"),
                new_data.get("views"),
                new_data.get("videos"),
            )

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    monitor()
