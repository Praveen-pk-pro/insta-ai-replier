from instagrapi import Client
import requests
import time
import os

USERNAME = os.getenv("INSTA_USERNAME")
PASSWORD = os.getenv("INSTA_PASSWORD")
FRIEND_USERNAME = os.getenv("FRIEND_INSTA")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

def get_ai_reply(user_message):
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
    }
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "Reply casually in Tanglish (Tamil + English mix)."},
            {"role": "user", "content": user_message}
        ]
    }
    res = requests.post(url, json=data, headers=headers)
    reply = res.json()["choices"][0]["message"]["content"]
    return reply.strip() + " (Replied by AI)"

cl = Client()
cl.login(USERNAME, PASSWORD)
print("✅ Logged in to Instagram")

last_seen_msg = None

while True:
    try:
        user_id = cl.user_id_from_username(FRIEND_USERNAME)
        threads = cl.direct_threads()
        for thread in threads:
            if thread.users[0].username == FRIEND_USERNAME:
                last_msg = thread.messages[0]
                if last_msg.id != last_seen_msg and last_msg.user_id != cl.user_id:
                    msg_text = last_msg.text
                    print(f"📩 New message from {FRIEND_USERNAME}: {msg_text}")
                    reply_text = get_ai_reply(msg_text)
                    print(f"🤖 Replying with: {reply_text}")
                    cl.direct_send(reply_text, [user_id])
                    last_seen_msg = last_msg.id
        time.sleep(15)
    except Exception as e:
        print("⚠️ Error:", e)
        time.sleep(30)
