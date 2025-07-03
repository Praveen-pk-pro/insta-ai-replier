from instagrapi import Client
import requests
import time
import os

USERNAME = os.getenv("INSTA_USERNAME")
PASSWORD = os.getenv("INSTA_PASSWORD")
FRIEND_USERNAME = os.getenv("FRIEND_INSTA")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
SESSION_FILE = "addition.json"

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
    try:
        res = requests.post(url, json=data, headers=headers)
        reply = res.json()["choices"][0]["message"]["content"]
        return reply.strip() + " (Replied by AI)"
    except Exception as e:
        print("❌ DeepSeek API Error:", e)
        return "Sorry, I can't reply right now. (Replied by AI)"

# Login using session if available
cl = Client()
try:
    cl.load_settings(SESSION_FILE)
    cl.login(USERNAME, PASSWORD)
    cl.dump_settings(SESSION_FILE)
    print("✅ Logged in with session")
except Exception as e:
    print("❌ Login failed:", e)
    exit()

# Get friend user ID
try:
    friend_user_id = cl.user_id_from_username(FRIEND_USERNAME)
except Exception as e:
    print("❌ Couldn't get friend ID:", e)
    exit()

print(f"🤖 Listening for messages from {FRIEND_USERNAME}...")

last_seen_msg_id = None

while True:
    try:
        threads = cl.direct_threads()
        for thread in threads:
            if thread.users[0].username != FRIEND_USERNAME:
                continue

            messages = cl.direct_messages(thread.id, amount=1)
            if not messages:
                continue

            msg = messages[0]
            if msg.id != last_seen_msg_id and msg.user_id == friend_user_id:
                print(f"📨 New message: {msg.text}")
                reply = get_ai_reply(msg.text)
                cl.direct_send(reply, [friend_user_id])
                print(f"✅ Sent reply: {reply}")
                last_seen_msg_id = msg.id

    except Exception as err:
        print("⚠️ Error:", err)

    time.sleep(15)
