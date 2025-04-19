import os
import json
import base64
import requests
import feedparser
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from nacl import encoding, public

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
    return response.json()

# GitHub Secretsを更新する関数（Libsodium で暗号化）
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

# LINEに通知を送信する関数
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
            message = f"📢{latest_title}\n{latest_link}"
            send_line_broadcast(message)
            update_secret(secret_key, latest_link)
        else:
            print(f"No update for {name}.")

# メインの実行
if __name__ == "__main__":
    main()
