import feedparser
import os
import requests
import json
import pytz
from datetime import datetime

# 環境変数からトークンを取得
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LAST_POST_URL = os.getenv("LAST_POST_URL")  # 環境変数から前回のURLを取得

# OpenAI APIキー設定
# openai.api_key = OPENAI_API_KEY

# 複数のRSS URLをここにリストで記述
rss_urls = [
    # @_ritsuki_hikaru
    "https://rss.app/feeds/LqP6Qvlf6WtxXyGS.xml",
    # @yanagi_miyu_official
    "https://rss.app/feeds/gGRbYTC3RVX3PPMa.xml"
]

# 通知履歴ファイル
last_post_file = "last_posts.json"

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

# コメント生成関数は一時的に無効化
# def generate_comment(title):
#     prompt = f"""
#     以下のTikTokの動画タイトルに対するコメントを1つ考えてください。
#     - コメント対象はアイドル
#     - 面白くて、印象に残る
#     - 短め（20文字以内）
#     - 基本は相手を褒める内容
#     - 誰も傷つけない内容

#     タイトル: {title}
#     コメント:
#     """
#     response = openai.ChatCompletion.create(
#         model="gpt-3.5-turbo",
#         messages=[{
#             "role": "user",
#             "content": prompt
#         }],
#         temperature=0.8,
#         max_tokens=60
#     )
#     return response.choices[0].message["content"].strip()

# 1時〜9時はスキップ
# 日本時間 (JST) のタイムゾーンを取得
japan_timezone = pytz.timezone('Asia/Tokyo')
# 日本時間で現在の時間を取得
current_hour = datetime.now(japan_timezone).hour
if 1 <= current_hour < 9:
    exit()

# 前回の投稿URLをチェック
if LAST_POST_URL:
    print(f"Last post URL: {LAST_POST_URL}")

# RSSフィードをチェック
for rss_url in rss_urls:
    feed = feedparser.parse(rss_url)
    if feed.entries:
        latest_entry = feed.entries[0]
        post_link = latest_entry.link
        user = rss_url.split("/")[-1]
        title = latest_entry.title

        # 既に通知した投稿はスキップ
        if LAST_POST_URL == post_link:
            print(f"Skipping post for {user} (link: {post_link})")  # デバッグ用ログ
            continue

        # 通知1: 投稿の情報
        info_message = f"📢 {title}\n{post_link}"
        send_line_broadcast(info_message)

        # コメント生成と通知2は無効化
        # comment = generate_comment(title)
        # comment_message = f"{comment}"
        # send_line_broadcast(comment_message)

        # 最後に通知したリンクを環境変数で更新（次回に反映）
        os.environ["LAST_POST_URL"] = post_link  # 新しいURLを環境変数に設定
