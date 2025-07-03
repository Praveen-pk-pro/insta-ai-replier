from instagrapi import Client
import requests
import time
import os
import random

# 🔐 Load environment variables
USERNAME = os.getenv("INSTA_U")
PASSWORD = os.getenv("INSTA_P")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SESSION_FILE = "addition.json"

# ✅ Load friend usernames from multiple env vars
raw_usernames = [
    os.getenv("INSTA", ""),
    os.getenv("STAR", ""),
    os.getenv("LOVEDONE", "")
]
FRIEND_USERNAMES = [u.strip() for u in raw_usernames if u.strip()]

# 🧠 Custom AI settings per friend
FRIEND_CONFIGS = {
    "mani246_": {
        "prompt": "Reply rude in English only. Never use Tamil or Tanglish.",
        "suffixes": [
            " (OTHA KENA PUNDA)",
            " (ENGA ENA YAN POOLA UMPURA)",
            " (DAI PUNDA)"
        ]
    },
    "praveen_apk06": {
        "prompt": "Reply casually in English.",
        "suffixes": [
            " (hey OWNER)",
            " (YOU STILL THINK ABOUT HER)",
            " (DO YOUR JOB)"," (Your absence echoes gently 🎧)", " (This moment breathes you in 💨)", " (You bloom in my quiet 🌸)", " (Your kindness stays in silence 🫶)", " (This stillness is full of you 🌙)", " (Your name rests in peace 💭)", " (You trace my every pause ✍️)", " (Love hums beneath your silence 🎶)", " (You slow the whole world down ⏳)", " (You speak where words fail 🫢)", " (You made quiet feel full 🤍)", " (You're tucked inside every calm ☁️)", " (Your presence balances my chaos ⚖️)", " (You soften every hard day 🧸)", " (There’s warmth where you exist 🔥)", " (My heart knows your silence 💓)", " (Love lingers in these pauses 🕊️)", " (You bring stillness to life 🎐)", " (There’s comfort in your quiet 🎧)", " (You're the peace I didn't know I needed 🕊️)", " (Everything quiet leads to you 🧭)", " (My peace wears your shape 🫶)", " (You’re always the softest thought 🛏️)", " (Your love doesn’t shout 💌)", " (You complete every quiet page 📖)", " (You're the calm I crave 🌙)", " (Even my thoughts look for you 🔎)", " (Where peace stays, so do you 🧘)", " (Your silence speaks louder to me 🎤)", " (Even in stillness, you arrive 💘)", " (You're hidden in every hush 🔇)", " (You're the meaning I breathe 💭)", " (Every quiet second holds you 💞)", " (You exist where noise fades 🧠)", " (I find you in soft places 💝)", " (You're the moment I wait for ⏱️)", " (You are what this quiet feels like 🤍)", " (You bring poetry to stillness ✍️)", " (Even empty space feels yours 📦)", " (The quiet doesn’t feel empty anymore 💓)", " (You made my thoughts softer 🫧)", " (Everything sounds softer since you 💫)", " (You melted into my rhythm 🎶)", " (You're what the quiet meant 💬)", " (Even the silence turns to you 🤍)", " (Love hid itself in you 🫶)", " (Peace only makes sense with you 🧘‍♂️)", " (You're the hush I trust 🤫)", " (Still moments carry your light 🔦)", " (You're the song beneath silence 🎧)", " (You echo through every slow breath 🌬️)"
            
        ]
    },
    "jaha_2312": {
        "prompt": "Reply poetically and warmly and lovely in English only.",
        "suffixes": [
            " (Your absence echoes gently 🎧)", " (This moment breathes you in 💨)", " (You bloom in my quiet 🌸)", " (Your kindness stays in silence 🫶)", " (This stillness is full of you 🌙)", " (Your name rests in peace 💭)", " (You trace my every pause ✍️)", " (Love hums beneath your silence 🎶)", " (You slow the whole world down ⏳)", " (You speak where words fail 🫢)", " (You made quiet feel full 🤍)", " (You're tucked inside every calm ☁️)", " (Your presence balances my chaos ⚖️)", " (You soften every hard day 🧸)", " (There’s warmth where you exist 🔥)", " (My heart knows your silence 💓)", " (Love lingers in these pauses 🕊️)", " (You bring stillness to life 🎐)", " (There’s comfort in your quiet 🎧)", " (You're the peace I didn't know I needed 🕊️)", " (Everything quiet leads to you 🧭)", " (My peace wears your shape 🫶)", " (You’re always the softest thought 🛏️)", " (Your love doesn’t shout 💌)", " (You complete every quiet page 📖)", " (You're the calm I crave 🌙)", " (Even my thoughts look for you 🔎)", " (Where peace stays, so do you 🧘)", " (Your silence speaks louder to me 🎤)", " (Even in stillness, you arrive 💘)", " (You're hidden in every hush 🔇)", " (You're the meaning I breathe 💭)", " (Every quiet second holds you 💞)", " (You exist where noise fades 🧠)", " (I find you in soft places 💝)", " (You're the moment I wait for ⏱️)", " (You are what this quiet feels like 🤍)", " (You bring poetry to stillness ✍️)", " (Even empty space feels yours 📦)", " (The quiet doesn’t feel empty anymore 💓)", " (You made my thoughts softer 🫧)", " (Everything sounds softer since you 💫)", " (You melted into my rhythm 🎶)", " (You're what the quiet meant 💬)", " (Even the silence turns to you 🤍)", " (Love hid itself in you 🫶)", " (Peace only makes sense with you 🧘‍♂️)", " (You're the hush I trust 🤫)", " (Still moments carry your light 🔦)", " (You're the song beneath silence 🎧)", " (You echo through every slow breath 🌬️)"
        ]
    }
}

# 🤖 Groq AI reply with random suffix
def get_ai_reply(user_message, prompt_text, suffix_text):
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {GROQ_API_KEY}"
        }
        data = {
            "model": "llama3-8b-8192",
            "messages": [
                {"role": "system", "content": prompt_text},
                {"role": "user", "content": user_message}
            ]
        }

        res = requests.post(url, headers=headers, json=data)
        res.raise_for_status()
        result = res.json()

        reply = result["choices"][0]["message"]["content"]
        print("🌐 Groq response:", reply)
        return reply.strip() + suffix_text

    except Exception as e:
        print("⚠️ Groq API failed:", e)
        return "Sorry, I can’t reply right now" + suffix_text

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
    for username in FRIEND_USERNAMES:
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

                friend_config = FRIEND_CONFIGS.get(username, {
                    "prompt": "Reply casually in English.",
                    "suffixes": [" (Replied by AI)"]
                })

                suffix = random.choice(friend_config["suffixes"])
                reply = get_ai_reply(msg.text, friend_config["prompt"], suffix)
                cl.direct_send(reply, [user_id])
                print(f"✅ Sent reply to {username}: {reply}")
                last_seen_msg_ids[user_id] = msg.id

    except Exception as err:
        print("⚠️ Error in loop:", err)

    time.sleep(3)
