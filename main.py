import requests
import openai
import os

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
LINE_NOTIFY_TOKEN = os.environ["LINE_NOTIFY_TOKEN"]
RSS_URL = os.environ["RSS_URL"]

STATE_FILE = "last_post.txt"

def fetch_latest_post_url():
    rss = requests.get(RSS_URL).text
    start = rss.find("<link>") + 6
    end = rss.find("</link>", start)
    return rss[start:end].strip()

def is_new_post(url):
    try:
        with open(STATE_FILE, "r") as f:
            last_url = f.read().strip()
    except FileNotFoundError:
        last_url = ""
    if url != last_url:
        with open(STATE_FILE, "w") as f:
            f.write(url)
        return True
    return False

def generate_comment(url):
    openai.api_key = OPENAI_API_KEY
    prompt = f"次のTikTok投稿に対して自然で面白い日本語コメントを一つ作ってください:\n{url}"
    res = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return res["choices"][0]["message"]["content"]

def send_line_notify(message):
    requests.post(
        "https://notify-api.line.me/api/notify",
        headers={"Authorization": f"Bearer {LINE_NOTIFY_TOKEN}"},
        data={"message": message}
    )

if __name__ == "__main__":
    url = fetch_latest_post_url()
    if is_new_post(url):
        comment = generate_comment(url)
        msg = f"【新しいTikTok投稿検知】\n{url}\n\nAIコメント案：\n{comment}"
        send_line_notify(msg)
