import feedparser
import os
import requests
import json
from datetime import datetime
import pytz

# ====== 時間による実行制御（JSTでAM1:00〜AM9:00はスキップ） ======
jst = pytz.timezone('Asia/Tokyo')
now = datetime.now(jst)
hour = now.hour

if 1 <= hour < 9:
    print("⏰ AM1:00〜AM9:00 の間なので処理をスキップします。")
    exit()

# ====== 環境変数からLINEトークンを取得 ======
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

# ====== 監視する複数のTikTokユーザーのRSS URL ======
rss_urls = [
    "https://rsshub.app/tiktok/user/_ritsuki_hikaru",
    "https://rsshub.app/tiktok/user/yanagi_miyu_official"
]

# ====== 最後に通知した投稿リンクの保存ファイル ======
last_post_file = "last_posts.json"

# ====== 最後の通知リンクを読み込み ======
def load_last_posts():
    if os.path.exists(last_post_file):
        with open(last_post_file, "r") as f:
            return json.load(f)
    return {}

# ====== 最後の通知リンクを保存 ======
def save_last_posts(last_posts):
    with open(last_post_file, "w") as f:
        json.dump(last_posts, f)

# ====== LINE一斉配信（Broadcast） ======
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

# ====== 実行ロジック ======
last_posts = load_last_posts()

for rss_url in rss_urls:
    feed = feedparser.parse(rss_url)
    if feed.entries:
        latest_entry = feed.entries[0]
        post_link = latest_entry.link
        user = rss_url.split("/")[-1]  # TikTokユーザー名
        title = latest_entry.title

        # 通知済みの場合はスキップ
        if last_posts.get(user) == post_link:
            continue

        # 新規投稿をLINEで通知
        message = f"📢 {user} の新着投稿がありました！\n{title}\n{post_link}"
        send_line_broadcast(message)

        # 通知済みリンクを保存
        last_posts[user] = post_link
        save_last_posts(last_posts)
