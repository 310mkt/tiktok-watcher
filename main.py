import feedparser
import requests
import os

RSS_URL = os.getenv("RSS_URL")
LINE_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

# 新着チェック用に保存ファイル
HISTORY_FILE = "latest_video.txt"

def get_latest_video_url():
    feed = feedparser.parse(RSS_URL)
    if feed.entries:
        return feed.entries[0].link
    return None

def is_new_video(latest_url):
    if not os.path.exists(HISTORY_FILE):
        return True
    with open(HISTORY_FILE, "r") as f:
        saved_url = f.read().strip()
    return saved_url != latest_url

def save_latest_video(url):
    with open(HISTORY_FILE, "w") as f:
        f.write(url)

def send_broadcast_message(text):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_TOKEN}"
    }
    payload = {
        "messages": [{
            "type": "text",
            "text": text
        }]
    }
    r = requests.post("https://api.line.me/v2/bot/message/broadcast", headers=headers, json=payload)
    print(f"Sent! Status: {r.status_code}, Response: {r.text}")

def main():
    latest_url = get_latest_video_url()
    if latest_url and is_new_video(latest_url):
        send_broadcast_message(f"新しいTikTok動画が投稿されました！\n{latest_url}")
        save_latest_video(latest_url)
    else:
        print("新着動画なし")

if __name__ == "__main__":
    main()
