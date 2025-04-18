import feedparser
import os
import requests

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

# 複数のRSS URLをここにリストで記述
rss_urls = [
    "https://rsshub.app/tiktok/user/_ritsuki_hikaru",
    "https://rsshub.app/tiktok/user/yanagi_miyu_official"
]

def send_line_broadcast(message):
    url = "https://api.line.me/v2/bot/message/broadcast"
    headers = {
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messages": [{
            "type": "text",
            "text": message
        }]
    }
    requests.post(url, headers=headers, json=data)

# 各RSSをチェック
for rss_url in rss_urls:
    feed = feedparser.parse(rss_url)
    if feed.entries:
        latest_entry = feed.entries[0]
        title = latest_entry.title
        link = latest_entry.link
        user = rss_url.split("/")[-1]  # ユーザー名抽出
        message = f"📢 {user} の新着投稿がありました！\n{title}\n{link}"
        send_line_broadcast(message)
