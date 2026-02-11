import requests
import asyncio
from telegram import Bot

# ====== ใส่ค่าใหม่ของคุณตรงนี้ ======
TOKEN = "8538417344:AAELrbI2KX9JmhHi_EhgCxLXPfPqyl8E29Q"
CHAT_ID = "1003882788938"
API_KEY = "AIzaSyB6wTJ74st9Q-MGWYFpNATxZ3ghHbgokpM"

CHANNEL_HANDLES = [
    "JOJOCARTOON-p7p",
    "Rasingcartoon",
    "RonaldoNo1-j6j",
    "Iconiccartoon-y5i"
]
# ======================================

bot = Bot(token=TOKEN)

channel_status = {}


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


async def check_channels():
    global channel_status

    for handle in CHANNEL_HANDLES:
        channel_id = get_channel_id(handle)

        if channel_id:
            status = "alive"
        else:
            status = "dead"

        if handle not in channel_status:
            channel_status[handle] = status
            continue

        if status != channel_status[handle]:

            if status == "alive":
                message = f"✅ {handle} ยังอยู่ปกติ"
            else:
                message = f"🚨 {handle} อาจโดนระงับ / ค้นหาไม่พบ"

            await bot.send_message(chat_id=CHAT_ID, text=message)

            channel_status[handle] = status


async def main():
    while True:
        await check_channels()
        await asyncio.sleep(300)  # เช็คทุก 5 นาที


asyncio.run(main())
