import os
import requests
import openai
import time

# 環境変数からトークン取得
LINE_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# タイトル（仮の投稿タイトル）
title = "新しいダンス動画を投稿しました🕺🔥"

# OpenAIにコメント生成依頼
openai.api_key = OPENAI_API_KEY

# プロンプトの組み立て
prompt = f"""
以下のTikTokの動画タイトルに対するコメントを1つ考えてください。
- コメント対象はアイドル
- 面白くて、印象に残る
- 短め（20文字以内）
- 基本は相手を褒める内容
- 誰も傷つけない内容

タイトル: {title}
コメント:
"""

# リトライ回数と待機時間
retries = 1
wait_time = 5

for attempt in range(retries):
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            temperature=0.7,
            max_tokens=60,
            n=1,
            stop=None
        )
        comment = response.choices[0].text.strip()
        break
    except openai.error.RateLimitError as e:
        print(f"Rate limit exceeded, retrying... ({attempt+1}/{retries})")
        if attempt == retries - 1:
            print("Max retries exceeded, exiting.")
            raise e
        time.sleep(wait_time)

# LINEでコメントを通知
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

# LINEに送信（2通送る）
send_line_broadcast(f"📢 新しい投稿タイトル: {title}")
send_line_broadcast(f"💬 自動返信コメント: {comment}")
