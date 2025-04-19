import os
import json
import requests
from TikTokApi import TikTokApi

# LINE設定
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

# ユーザーごとの設定
tiktok_users = {
    "ritsuki": {
        "sec_uid": os.getenv("SEC_UID_RITSUKI"),
        "last_id": os.getenv("LAST_POST_ID_RITSUKI"),
        "secret_name": "LAST_POST_ID_RITSUKI"
    },
    "yanagi": {
        "sec_uid": os.getenv("SEC_UID_YANAGI"),
        "last_id": os.getenv("LAST_POST_ID_YANAGI"),
        "secret_name": "LAST_POST_ID_YANAGI"
    }
}

GITHUB_REPO = os.environ["GITHUB_REPOSITORY"]
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

# 公開鍵取得
def get_public_key():
    url = f"https://api.github.com/repos/{GITHUB_REPO}/actions/secrets/public-key"
    res = requests.get(url, headers=HEADERS)
    res.raise_for_status()
    return res.json()

# シークレット更新
from nacl import encoding, public
def update_secret(secret_name, value):
    key_info = get_public_key()
    pk = public.PublicKey(key_info["key"].encode("utf-8"), encoding.Base64Encoder())
    box = public.SealedBox(pk)
    encrypted_value = box.encrypt(value.encode("utf-8"))
    encrypted_b64 = base64.b64encode(encrypted_value).decode("utf-8")

    url = f"https://api.github.com/repos/{GITHUB_REPO}/actions/secrets/{secret_name}"
    res = requests.put(url, headers=HEADERS, json={
        "encrypted_value": encrypted_b64,
        "key_id": key_info["key_id"]
    })
    res.raise_for_status()

# LINE通知
def send_line_broadcast(msg):
    url = "https://api.line.me/v2/bot/message/broadcast"
    headers = {
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messages": [{
            "type": "text",
            "text": msg
        }]
    }
    res = requests.post(url, headers=headers, json=data)
    res.raise_for_status()

# メイン処理
def main():
    with TikTokApi() as api:
        for name, info in tiktok_users.items():
            sec_uid = info["sec_uid"]
            secret_key = info["secret_name"]
            last_post_id = info["last_id"]

            user_videos = api.user(sec_uid=sec_uid).videos(count=1)
            if not user_videos:
                continue

            latest_video = user_videos[0]
            latest_id = latest_video.id
            latest_desc = latest_video.desc
            latest_url = f"https://www.tiktok.com/@{name}/video/{latest_id}"

            if latest_id != last_post_id:
                message = f"📢 {name}:\n{latest_desc}\n{latest_url}"
                send_line_broadcast(message)
                update_secret(secret_key, latest_id)
            else:
                print(f"No update for {name}")

if __name__ == "__main__":
    main()
