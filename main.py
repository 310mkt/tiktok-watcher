import feedparser
import os
import requests
import json

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

# 複数のRSS URLをここにリストで記述
rss_urls = [
    "https://rsshub.app/tiktok/user/_ritsuki_hikaru",
    "https://rsshub.app/tiktok/user/yanagi_miyu_official"
]

# 最後に通知した投稿のリンクを保存するファイル
last_post_file = "last_posts.json"

# 保存されたデータを読み込み
def load_last_posts():
    if os.path.exists(last_post_file):
        with open(last_post_file, "r") as f:
            return json.load(f)
    return {}

# データを保存
def save_last_posts(last_posts):
    with open(last_post_file, "w") as f:
        json.dump(last_posts, f)

# LINEへの一律配信
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

# すでに通知した投稿リンクを保持する辞書
last_posts = load_last_posts()

# 各RSSをチェック
for rss_url in rss_urls:
    feed = feedparser.parse(rss_url)
    if feed.entries:
        latest_entry = feed.entries[0]
        post_link = latest_entry.link
        user = rss_url.split("/")[-1]  # ユーザー名抽出
        title = latest_entry.title

        # すでに同じリンクが通知されていればスキップ
        if last_posts.get(user) == post_link:
            continue

        # 新しい投稿の場合、LINE通知
        message = f"📢 {user} の新着投稿がありました！\n{title}\n{post_link}"
        send_line_broadcast(message)

        # 最後に通知した投稿のリンクを保存
        last_posts[user] = post_link
        save_last_posts(last_posts)
