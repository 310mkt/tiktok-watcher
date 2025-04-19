import os
import requests
import feedparser

# RSSフィードとGitHub Secretsの対応
rss_map = {
    "ritsuki_hikaru": {
        "url": "https://rss.app/feeds/LqP6Qvlf6WtxXyGS.xml",
        "secret": "LAST_POST_RITSUKI"
    },
    "yanagi_miyu": {
        "url": "https://rss.app/feeds/gGRbYTC3RVX3PPMa.xml",
        "secret": "LAST_POST_MIYU"
    }
}

GITHUB_REPO = os.getenv("GITHUB_REPO")
GITHUB_TOKEN = os.getenv("GH_PAT")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

def get_secret(secret_name):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/actions/secrets/{secret_name}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        return res.json().get("value")
    return None

def update_secret(secret_name, secret_value):
    import base64
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import padding
    from cryptography.hazmat.primitives import hashes

    # GitHubの公開鍵を取得
    pubkey_url = f"https://api.github.com/repos/{GITHUB_REPO}/actions/secrets/public-key"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    pubkey_res = requests.get(pubkey_url, headers=headers).json()
    key_id = pubkey_res["key_id"]
    public_key = base64.b64decode(pubkey_res["key"])

    # RSA暗号化
    encrypted = rsa.encrypt(
        secret_value.encode(),
        rsa.RSAPublicNumbers(65537, int.from_bytes(public_key, 'big')).public_key()
    )

    encrypted_value = base64.b64encode(encrypted).decode()

    payload = {
        "encrypted_value": encrypted_value,
        "key_id": key_id
    }
    secret_url = f"https://api.github.com/repos/{GITHUB_REPO}/actions/secrets/{secret_name}"
    res = requests.put(secret_url, headers=headers, json=payload)
    return res.status_code in [200, 201]

def send_line_broadcast(message):
    headers = {
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messages": [{"type": "text", "text": message}]
    }
    requests.post("https://api.line.me/v2/bot/message/broadcast", headers=headers, json=data)

for name, data in rss_map.items():
    feed = feedparser.parse(data["url"])
    if not feed.entries:
        continue

    latest_link = feed.entries[0].link
    last_link = get_secret(data["secret"])

    if latest_link != last_link:
        title = feed.entries[0].title
        send_line_broadcast(f"📢 {title}\n{latest_link}")
        update_secret(data["secret"], latest_link)
