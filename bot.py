import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json
import os

# ================= SETTINGS =================
TOKEN = "8629584902:AAEuAPMIW6V0eTaRRxxwvmWT7EMbGl3r3zU"
ADMIN_ID = 7156406347   # 👉 तुझा numeric Telegram ID
ADMIN_USERNAME = "Taskman96"  # @ नको
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

def add_user(user_id):
    users = load_users()
    if user_id not in users:
        users.append(user_id)
        save_users(users)

# ---------- START ----------
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    add_user(user_id)

    markup = InlineKeyboardMarkup()
    free_btn = InlineKeyboardButton("🔓 Free Channel", url=FREE_CHANNEL_LINK)
    premium_btn = InlineKeyboardButton("💎 Premium Channel", callback_data="premium")

    markup.add(free_btn)
    markup.add(premium_btn)

    bot.send_message(
        message.chat.id,
        "🔥 *WELCOME TO MY BOT* 🔥\n\n"
        "🎬 *ALL ACTORS VIRAL MMS* 🎬\n\n"
        "👇 Choose Option Below 👇",
        parse_mode="Markdown",
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
        f"💎 *PREMIUM ACCESS*\n\n"
        f"🔥 *ALL ACTORS VIRAL MMS* 🔥\n\n"
        f"💰 Price: {PRICE}",
        parse_mode="Markdown",
        reply_markup=markup
    )

# ---------- USER COUNT ----------
@bot.message_handler(commands=['users'])
def user_count(message):
    if message.from_user.id == ADMIN_ID:
        users = load_users()
        bot.send_message(message.chat.id, f"📊 Total Users: {len(users)}")

# ---------- BROADCAST ----------
@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    if message.from_user.id == ADMIN_ID:
        text = message.text.replace("/broadcast ", "")
        users = load_users()
        for user in users:
            try:
                bot.send_message(user, f"📢 {text}")
            except:
                pass
        bot.send_message(message.chat.id, "✅ Broadcast Sent!")

# ---------- RUN ----------
print("🔥 Bot Running Successfully 🔥")
bot.infinity_polling()

