import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json
import os

# ================= SETTINGS =================
TOKEN = "8629584902:AAEuAPMIW6V0eTaRRxxwvmWT7EMbGl3r3zU"
ADMIN_ID = 7156406347
ADMIN_USERNAME = "Taskman96"
FREE_CHANNEL_LINK = "https://t.me/viral_video_mms_96"
PRICE = "₹30"
# ============================================

bot = telebot.TeleBot(TOKEN)

USERS_FILE = "users.json"

# ---------- USER DATABASE ----------
def load_users():
    if not os.path.exists(USERS_FILE):
        return []
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

def add_user(user):
    users = load_users()

    user_data = {
        "id": user.id,
        "name": user.first_name,
        "username": user.username if user.username else "NoUsername"
    }

    if not any(u["id"] == user.id for u in users):
        users.append(user_data)
        save_users(users)

# ---------- START ----------
@bot.message_handler(commands=['start'])
def start(message):
    add_user(message.from_user)

    markup = InlineKeyboardMarkup()
    free_btn = InlineKeyboardButton("🔓 Free Channel", url=FREE_CHANNEL_LINK)
    premium_btn = InlineKeyboardButton("💎 Premium Channel", callback_data="premium")

    markup.add(free_btn)
    markup.add(premium_btn)

    bot.send_message(
        message.chat.id,
        "Welcome 👋\n\n"
        "Choose your access type below.",
        reply_markup=markup
    )

# ---------- PREMIUM ----------
@bot.callback_query_handler(func=lambda call: call.data == "premium")
def premium(call):
    markup = InlineKeyboardMarkup()
    dm_btn = InlineKeyboardButton(
        "📩 DM For Payment",
        url=f"https://t.me/{ADMIN_USERNAME}"
    )
    markup.add(dm_btn)

    bot.send_message(
        call.message.chat.id,
        f"💎 PREMIUM ACCESS\n\n"
        f"💰 Price: {PRICE}",
        reply_markup=markup
    )

# ---------- TOTAL USERS ----------
@bot.message_handler(commands=['users'])
def user_count(message):
    if message.from_user.id == ADMIN_ID:
        users = load_users()
        bot.send_message(message.chat.id, f"📊 Total Users: {len(users)}")

# ---------- USER LIST ----------
@bot.message_handler(commands=['list'])
def list_users(message):
    if message.from_user.id == ADMIN_ID:
        users = load_users()
        if not users:
            bot.send_message(message.chat.id, "No users found.")
            return

        text = "📋 User List:\n\n"
        for user in users:
            text += f"{user['name']} (@{user['username']}) - {user['id']}\n"

        # Telegram limit 4096 chars, so split if needed
        for i in range(0, len(text), 4000):
            bot.send_message(message.chat.id, text[i:i+4000])

# ---------- BROADCAST ----------
@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    if message.from_user.id == ADMIN_ID:
        text = message.text.replace("/broadcast ", "")
        users = load_users()
        sent = 0

        for user in users:
            try:
                bot.send_message(user["id"], f"📢 {text}")
                sent += 1
            except:
                pass

        bot.send_message(message.chat.id, f"✅ Broadcast Sent to {sent} users!")

# ---------- RUN ----------
print("🔥 Bot Running Successfully 🔥")
bot.infinity_polling()
