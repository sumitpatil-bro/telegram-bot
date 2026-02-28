import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json
import os

# ================= SETTINGS =================
TOKEN = "8629584902:AAEuAPMIW6V0eTaRRxxwvmWT7EMbGl3r3zU"
ADMIN_ID = 7156406347
ADMIN_USERNAME = "Taskman96"

FREE_CHANNEL_LINK = "https://t.me/+GFi7yL9PNqhlN2I1"
PREMIUM_CHANNEL_LINK = "https://t.me/+WIBBIo-JaMljZjM1"

PRICE = "₹30"
QR_FILE = "payment_qr.png"
USERS_FILE = "users.json"
# ============================================

bot = telebot.TeleBot(TOKEN)
pending_payments = {}

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
    if not any(u["id"] == user.id for u in users):
        users.append({
            "id": user.id,
            "name": user.first_name,
            "username": user.username if user.username else "NoUsername",
            "premium": False
        })
        save_users(users)

def give_premium(user_id):
    users = load_users()
    for u in users:
        if u["id"] == user_id:
            u["premium"] = True
    save_users(users)

# ---------- START ----------
@bot.message_handler(commands=['start'])
def start(message):
    add_user(message.from_user)

    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("🔓 Free Channel", url=FREE_CHANNEL_LINK),
        InlineKeyboardButton("💎 Buy Premium", callback_data="premium")
    )

    bot.send_message(
        message.chat.id,
        "Welcome 👋\n\nChoose your access type below.",
        reply_markup=markup
    )

# ---------- PREMIUM BUTTON ----------
@bot.callback_query_handler(func=lambda call: call.data == "premium")
def premium(call):
    bot.answer_callback_query(call.id)

    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("📩 Contact Admin", url=f"https://t.me/{ADMIN_USERNAME}")
    )

    if os.path.exists(QR_FILE):
        with open(QR_FILE, "rb") as photo:
            bot.send_photo(
                call.message.chat.id,
                photo,
                caption=f"💎 PREMIUM ACCESS\n\n💰 Price: {PRICE}\n\n📌 Scan QR and pay.\nSend payment screenshot here.",
                reply_markup=markup
            )
    else:
        bot.send_message(
            call.message.chat.id,
            f"⚠ QR file not found!\n\n💰 Price: {PRICE}\nSend screenshot after payment.",
            reply_markup=markup
        )

# ---------- CAPTURE SCREENSHOT ----------
@bot.message_handler(content_types=['photo'])
def screenshot_handler(message):
    user_id = message.from_user.id

    users = load_users()
    user = next((u for u in users if u["id"] == user_id), None)

    if user and user["premium"]:
        bot.send_message(user_id, "✅ You already have premium access.")
        return

    file_id = message.photo[-1].file_id
    pending_payments[user_id] = file_id

    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user_id}"),
        InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user_id}")
    )

    username = message.from_user.username if message.from_user.username else "NoUsername"

    bot.send_photo(
        ADMIN_ID,
        file_id,
        caption=f"Payment screenshot from {message.from_user.first_name} (@{username})",
        reply_markup=markup
    )

    bot.send_message(user_id, "📨 Screenshot received. Wait for admin approval.")

# ---------- ADMIN DECISION ----------
@bot.callback_query_handler(func=lambda call: call.data.startswith("approve_") or call.data.startswith("reject_"))
def admin_decision(call):

    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "Not authorized")
        return

    action, user_id = call.data.split("_")
    user_id = int(user_id)

    if action == "approve":
        give_premium(user_id)
        bot.send_message(
            user_id,
            f"✅ Payment Approved!\n\nJoin Premium:\n{PREMIUM_CHANNEL_LINK}"
        )
        bot.answer_callback_query(call.id, "Approved")

    elif action == "reject":
        bot.send_message(
            user_id,
            "❌ Payment Rejected. Contact admin."
        )
        bot.answer_callback_query(call.id, "Rejected")

# ---------- ADMIN COMMANDS ----------
@bot.message_handler(commands=['users'])
def user_count(message):
    if message.from_user.id == ADMIN_ID:
        users = load_users()
        bot.send_message(message.chat.id, f"📊 Total Users: {len(users)}")

@bot.message_handler(commands=['list'])
def list_users(message):
    if message.from_user.id == ADMIN_ID:
        users = load_users()
        if not users:
            bot.send_message(message.chat.id, "No users found.")
            return

        text = "📋 User List:\n\n"
        for u in users:
            status = "Premium" if u["premium"] else "Free"
            text += f"{u['name']} (@{u['username']}) - {status}\n"

        for i in range(0, len(text), 4000):
            bot.send_message(message.chat.id, text[i:i+4000])

@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    if message.from_user.id == ADMIN_ID:
        text = message.text.replace("/broadcast ", "")
        users = load_users()
        sent = 0
        for u in users:
            try:
                bot.send_message(u["id"], f"📢 {text}")
                sent += 1
            except:
                pass

        bot.send_message(message.chat.id, f"✅ Broadcast sent to {sent} users!")

# ---------- RUN ----------
print("🔥 Bot Running Successfully 🔥")
bot.infinity_polling()

