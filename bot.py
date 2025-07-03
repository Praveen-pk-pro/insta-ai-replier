from instagrapi import Client
import requests
import time
import os

# 🔐 Load environment variables
USERNAME = os.getenv("INSTA_U")
PASSWORD = os.getenv("INSTA_P")
FRIEND_USERNAME = os.getenv("INSTA")
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
                {"role": "system", "content": "if it in english just Reply casually in English or if in tanglish just reply casually as a friend in tamil."},
                {"role": "user", "content": user_message}
            ]
        }

        res = requests.post(url, headers=headers, json=data)
        res.raise_for_status()
        result = res.json()

        reply = result["choices"][0]["message"]["content"]
        print("🌐 Groq response:", reply)
        return reply.strip() + " ( AI made by PK)"

    except Exception as e:
        print("⚠️ Groq API failed:", e)
        return "Sorry, I can’t reply right now (Replied by AI, made by PK)"

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

# 🔍 Get friend's user ID
try:
    friend_user_id = cl.user_id_from_username(FRIEND_USERNAME)
    print(f"🔍 Found user ID for {FRIEND_USERNAME}: {friend_user_id}")
except Exception as e:
    print("❌ Couldn't get friend ID:", e)
    exit()

print(f"🤖 Listening for messages from {FRIEND_USERNAME}...")

last_seen_msg_id = None

# 🔁 Auto-reply loop
while True:
    try:
        threads = cl.direct_threads()
        for thread in threads:
            if not thread.users or thread.users[0].username != FRIEND_USERNAME:
                continue

            messages = cl.direct_messages(thread.id, amount=1)
            if not messages:
                continue

            msg = messages[0]
            if msg.id != last_seen_msg_id and msg.user_id == friend_user_id:
                print(f"📨 New message: {msg.text}")
                
                # ✅ Always reply in English
                reply = get_ai_reply(msg.text)
                cl.direct_send(reply, [friend_user_id])
                print(f"✅ Sent reply: {reply}")
                last_seen_msg_id = msg.id

    except Exception as err:
        print("⚠️ Error in loop:", err)

    time.sleep(3)
