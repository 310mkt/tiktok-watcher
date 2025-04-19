import os
import json
import base64
import requests
import feedparser
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

# 定義（GitHubの情報）
GITHUB_REPO = os.environ["GITHUB_REPOSITORY"]
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

# LINE設定
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

# RSSの設定
rss_sources = {
    "RITSUKI": {
        "url": "https://rss.app/feeds/LqP6Qvlf6WtxXyGS.xml",
        "secret": "LAST_POST_RITSUKI"
    },
    "YANAGI": {
        "url": "https://rss.app/feeds/gGRbYTC3RVX3PPMa.xml",
        "secret": "LAST_POST_YANAGI"
    }
}

# GitHubから公開鍵を取得
def get_public_key():
    url = f"https://api.github.com/repos/{GITHUB_REPO}/actions/secrets/public-key"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    key_info = response.json()
    
    # レスポンスに公開鍵データが含まれているか確認
    print(f"Received public key: {key_info}")
    return key_info

# GitHub Secretsを更新する関数
def update_secret(secret_name, value):
    try:
        key_info = get_public_key()

        # 公開鍵のデコードとロード
        public_key_base64 = key_info["key"]
        print(f"Decoding public key...")  # デコード処理の確認
        public_key = serialization.load_pem_public_key(
            base64.b64decode(public_key_base64),
            backend=default_backend()
        )
        
        # 公開鍵でデータを暗号化
        encrypted = public_key.encrypt(
            value.encode(),
            padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
        )
        
        # 暗号化されたデータをbase64エンコード
        encrypted_value = base64.b64encode(encrypted).decode()
        
        # GitHubに暗号化されたシークレットを送信
        url = f"https://api.github.com/repos/{GITHUB_REPO}/actions/secrets/{secret_name}"
        response = requests.put(url, headers=HEADERS, json={
            "encrypted_value": encrypted_value,
            "key_id": key_info["key_id"]
        })
        response.raise_for_status()

        print(f"Secret {secret_name} updated successfully.")
    except Exception as e:
        print(f"Error updating secret {secret_name}: {e}")
        raise

# LINEに通知を送信する関数
def send_line_broadcast(message):
    try:
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

        print("LINE notification sent successfully.")
    except Exception as e:
        print(f"Error sending LINE notification: {e}")
        raise

# メインの処理
def main():
    for name, data in rss_sources.items():
        rss_url = data["url"]
        secret_key = data["secret"]
        feed = feedparser.parse(rss_url)
        
        if not feed.entries:
            continue

        latest_entry = feed.entries[0]
        latest_link = latest_entry.link
        latest_title = latest_entry.title

        # GitHub Secrets から現在の値を取得
        current_value = os.getenv(secret_key)

        # 最新のURLと保存されているURLが異なればLINE通知を送信し、Secretsを更新
        if current_value != latest_link:
            message = f"📢 {name}:\n{latest_title}\n{latest_link}"
            send_line_broadcast(message)
            update_secret(secret_key, latest_link)
        else:
            print(f"No update for {name}.")

# メインの実行
if __name__ == "__main__":
    main()
