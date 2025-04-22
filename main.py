import os
import base64
import requests
import asyncio
import random
import time
from TikTokApi import TikTokApi
from nacl import encoding, public

# GitHub API設定
GITHUB_REPO = os.environ["GITHUB_REPOSITORY"]
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

# TikTokユーザー設定
tiktok_users = {
    "RITSUKI": {
        "sec_uid": "MS4wLjABAAAAQHbSXupM9HaW6UHNF62i1onY0yx_oqnGGMoSSMqvUSPmwrx48w9XbIrNK5klBqsV",
        "secret": "LAST_POST_RITSUKI"
    },
    "YANAGI": {
        "sec_uid": "MS4wLjABAAAAInbsNZdhBVMir_rYQ7nGuO3YRnkjBIMfi-mA0ggfe0fYpPAUodhafkKNCviSbCth",
        "secret": "LAST_POST_YANAGI"
    }
}

# GitHub secrets更新関数
def get_public_key():
    url = f"https://api.github.com/repos/{GITHUB_REPO}/actions/secrets/public-key"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def update_secret(secret_name, value):
    key_info = get_public_key()
    public_key = public.PublicKey(key_info["key"].encode("utf-8"), encoding.Base64Encoder())
    sealed_box = public.SealedBox(public_key)
    encrypted_value = base64.b64encode(sealed_box.encrypt(value.encode("utf-8"))).decode("utf-8")
    url = f"https://api.github.com/repos/{GITHUB_REPO}/actions/secrets/{secret_name}"
    response = requests.put(url, headers=HEADERS, json={
        "encrypted_value": encrypted_value,
        "key_id": key_info["key_id"]
    })
    response.raise_for_status()

# LINE通知関数
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
    response.raise_for_status()

# メイン処理
async def main():
    async with TikTokApi() as api:
        # ヘッドレスモードオフ、ブラウザ表示
        await api.create_sessions(
            num_sessions=1,
            browser="webkit",  # 使用するブラウザ
            headless=False,  # ヘッドレスモードをオフに
            browser_args=[
                "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            ]
        )
        
        # ユーザーごとに動画を取得し、更新を確認
        for name, data in tiktok_users.items():
            sec_uid = data["sec_uid"]
            secret_key = data["secret"]

            user = api.user(sec_uid=sec_uid)
            videos = [video async for video in user.videos(count=1)]

            if not videos:
                print(f"No videos for {name}.")
                continue

            latest_video = videos[0]
            latest_url = f"https://www.tiktok.com/@{user.username}/video/{latest_video.id}"
            current_value = os.getenv(secret_key)

            # URLが更新されている場合にLINE通知とGitHub Secrets更新
            if current_value != latest_url:
                message = f"📢 {name}:\n{latest_video.desc}\n{latest_url}"
                send_line_broadcast(message)
                update_secret(secret_key, latest_url)
            else:
                print(f"No update for {name}.")
            
            # ランダムな待機時間を設定
            time.sleep(random.uniform(1, 5))  # 1秒から5秒の間でランダムに待機

if __name__ == "__main__":
    asyncio.run(main())
