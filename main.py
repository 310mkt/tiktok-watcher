import os
import requests
import feedparser
from openai import OpenAI

RSS_URL = os.getenv("RSS_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_USER_ID = os.getenv("LINE_USER_ID")

client = OpenAI(api_key=OPENAI_API_KEY)

# 過去動画の記録（GitHub Actionsでは毎回消えるため、代替手段が必要）
seen_ids_file = "seen_ids.txt"
if os.path.exists(seen_ids_file):
    with open(seen_ids_file, "r") as f:
        seen_ids = set(f.read().splitlines())
else:
    seen_ids = set()

feed = feedparser.parse(RSS_URL)
new_videos = []

for entry in feed.entries:
    if entry.id not in seen_ids:
        new_videos.append(entry)
        seen_ids.add(entry.id)

if not new_videos:
    print("新着なし")
    exit()

for entry in new_videos:
    prompt = f"この動画の内容に合う自然な日本語のコメントを作成してください：{entry.title}"
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    comment = response.choices[0].message.content.strip()

    # LINE通知（Messaging API）
    requests.post(
        "https://api.line.me/v2/bot/message/push",
        headers={
            "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        },
        json={
            "to": LINE_USER_ID,
            "messages": [{"type": "text", "text": f"{entry.title}\n{comment}\n{entry.link}"}]
        }
    )

# 更新されたIDを保存
with open(seen_ids_file, "w") as f:
    f.write("\n".join(seen_ids))
