import os
import requests
import openai
import time

# OpenAIクライアントの初期化（v1以降の新方式）
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

LINE_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
title = "新しいダンス動画を投稿しました🕺🔥"

retries = 5
wait_time = 20

for attempt in range(retries):
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "あなたはTikTok動画に対する短くて面白くて優しい返信コメントを考えるアシスタントです。"},
                {"role": "user", "content": f"この投稿タイトルにコメントをつけて: 「{title}」"}
            ],
            temperature=0.8,
            max_tokens=60
        )
        comment = response.choices[0].message.content.strip()
        break
    except openai.RateLimitError:
        print(f"Rate limit exceeded, retrying... ({attempt+1}/{retries})")
        if attempt == retries - 1:
            raise
        time.sleep(wait_time)

# LINE通知
def send_line_broadcast(message):
    url = "https://api.line.me/v2/bot/message/broadcast"
    headers = {
        "Authorization": f"Bearer {LINE_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messages": [{
            "type": "text",
            "text": message
        }]
    }
    res = requests.post(url, headers=headers, json=data)
    print("Status:", res.status_code)
    print("Response:", res.text)

send_line_broadcast(f"📢 新しい投稿タイトル: {title}")
send_line_broadcast(f"💬 自動返信コメント: {comment}")
