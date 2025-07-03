from instagrapi import Client
import requests
import time
import os

# 🔐 Load environment variables
USERNAME = os.getenv("INSTA_U")
PASSWORD = os.getenv("INSTA_P")
FRIEND_USERNAMES = os.getenv("INSTA", "STAR")  # comma-separated usernames
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SESSION_FILE = "addition.json"

# 🤖 AI reply in English only
def get_ai_reply(user_message):
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {GROQ_API_KEY}"
        }
        data = {
            "model": "llama3-8b-8192",
            "messages": [
                {"role": "system", "content": "Reply casually in English only. Never use Tamil or Tanglish."},
                {"role": "user", "content": user_message}
            ]
        }

        res = requests.post(url, headers=headers, json=data)
        res.raise_for_status()
        result = res.json()

        reply = result["choices"][0]["message"]["content"]
        print("🌐 Groq response:", reply)
        return reply.strip() + "dai 9thu star punda "

    except Exception as e:
        print("⚠️ Groq API failed:", e)
        return "Sorry, I can’t reply to you star )"

# 📲 Instagram Login
cl = Client()
try:
    cl.load_settings(SESSION_FILE)
    cl.login(USERNAME, PASSWORD)
    cl.dump_settings(SESSION_FILE)
    print("✅ Logged in with session")
except Exception as e:
    print("❌ Login failed:", e)
    exit()

# 🔍 Get multiple friends' user IDs
friend_user_ids = {}
try:
    for username in FRIEND_USERNAMES.split(","):
        username = username.strip()
        if username:
            uid = cl.user_id_from_username(username)
            friend_user_ids[uid] = username
            print(f"🔍 Found user ID for {username}: {uid}")
except Exception as e:
    print("❌ Couldn't get one or more friend IDs:", e)
    exit()

print(f"🤖 Listening for messages from: {list(friend_user_ids.values())}")

last_seen_msg_ids = {}

# 🔁 Auto-reply loop
while True:
    try:
        threads = cl.direct_threads()
        for thread in threads:
            for user in thread.users:
                username = user.username
                user_id = user.pk

                if user_id not in friend_user_ids:
                    continue

                messages = cl.direct_messages(thread.id, amount=1)
                if not messages:
                    continue

                msg = messages[0]
                if msg.user_id != user_id:
                    continue

                last_seen = last_seen_msg_ids.get(user_id)
                if msg.id == last_seen:
                    continue

                print(f"📨 New message from {username}: {msg.text}")

                reply = get_ai_reply(msg.text)
                cl.direct_send(reply, [user_id])
                print(f"✅ Sent reply to {username}: {reply}")
                last_seen_msg_ids[user_id] = msg.id

    except Exception as err:
        print("⚠️ Error in loop:", err)

    time.sleep(3)
