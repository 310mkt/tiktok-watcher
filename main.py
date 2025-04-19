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

def get_public_key():
    url = f"https://api.github.com/repos/{GITHUB_REPO}/actions/secrets/public-key"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def update_secret(secret_name, value):
    key_info = get_public_key()
    public_key = serialization.load_pem_public_key(
        base64.b64decode(key_info["key"]),
        backend=default_backend()
    )
    encrypted = public_key.encrypt(
        value.encode(),
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
    )
    encrypted_value = base64.b64encode(encrypted).decode()
    url = f"https://api.github.com/repos/{GITHUB_REPO}/actions/secrets/{secret_name}"
    response = requests.put(url, headers=HEADERS, json={
        "encrypted_value": encrypted_value,
        "key_id": key_info["key_id"]
    })
    response.raise_for_status()

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

        if current_value != latest_link:
            message = f"📢 {name}:\n{latest_title}\n{latest_link}"
            send_line_broadcast(message)
            update_secret(secret_key, latest_link)
        else:
            print(f"No update for {name}.")

if __name__ == "__main__":
    main()
