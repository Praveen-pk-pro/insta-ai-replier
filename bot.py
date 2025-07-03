from instagrapi import Client
import google.generativeai as genai
import time
import os

# Load env variables
USERNAME = os.getenv("INSTA_U")
PASSWORD = os.getenv("INSTA_P")
FRIEND_USERNAME = os.getenv("INSTA")
GEMINI_API_KEY = os.getenv("INTAKEY")  # Now used as Gemini key
SESSION_FILE = "addition.json"

# 🧠 Gemini AI reply function
def get_ai_reply(user_message):
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-pro")

        prompt = f"Reply casually in Tanglish (Tamil + English mix): {user_message}"
        response = model.generate_content(prompt)
        print("🌐 Gemini reply:", response.text)
        return response.text.strip() + " (Replied by AI)"
    except Exception as e:
        print("⚠️ Gemini API failed:", e)
        return "Sorry, I can’t reply right now (Replied by AI)"

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

# 🔍 Get friend user ID
try:
    friend_user_id = cl.user_id_from_username(FRIEND_USERNAME)
    print(f"🔍 Found user ID for {FRIEND_USERNAME}: {friend_user_id}")
except Exception as e:
    print("❌ Couldn't get friend ID:", e)
    exit()

print(f"🤖 Listening for messages from {FRIEND_USERNAME}...")

last_seen_msg_id = None

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
                reply = get_ai_reply(msg.text)
                cl.direct_send(reply, [friend_user_id])
                print(f"✅ Sent reply: {reply}")
                last_seen_msg_id = msg.id

    except Exception as err:
        print("⚠️ Error in loop:", err)

    time.sleep(15)
