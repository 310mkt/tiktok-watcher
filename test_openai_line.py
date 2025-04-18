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

# リトライ回数を増やし、待機時間を長く
retries = 10  # リトライ回数を増やす
wait_time = 30  # 待機時間を30秒に変更

for attempt in range(retries):
    try:
        response = openai.ChatCompletion.create(  # 新しいAPIを使用
            model="gpt-3.5-turbo",  # または最新のモデル
            messages=[
                {"role": "system", "content": "あなたはTikTokに投稿された動画への面白くて短くて印象に残る、でも誰も傷つけない返信コメントを考えるアシスタントです。"},
                {"role": "user", "content": f"この投稿タイトルに返信するコメントを考えて: 「{title}」"}
            ],
            max_tokens=60,
            temperature=0.7
        )

        # コメントを取得
        comment = response['choices'][0]['message']['content'].strip()
        break  # 成功した場合、ループを抜ける
    except openai.error.RateLimitError as e:
        print(f"Rate limit exceeded, retrying... ({attempt+1}/{retries})")
        if attempt == retries - 1:  # 最後のリトライで失敗した場合
            print("Max retries exceeded, exiting.")
            raise e
        time.sleep(wait_time)  # 待機時間を30秒に変更

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
