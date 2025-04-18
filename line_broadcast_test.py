import os
import requests

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

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
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print("✅ Broadcast message sent successfully!")
    else:
        print(f"❌ Error: {response.status_code}, {response.text}")

send_line_broadcast("GitHub Actions から LINE Broadcast テスト通知！")
