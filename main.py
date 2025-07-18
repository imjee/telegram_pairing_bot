import os
import json
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
PAIRINGS_FILE = os.path.join(DATA_DIR, "pairings.json")
REPORTS_FILE = os.path.join(DATA_DIR, "reports.json")
BLOCKED_FILE = os.path.join(DATA_DIR, "blocked.json")
VIP_FILE = os.path.join(DATA_DIR, "vip.json")

for file in [USERS_FILE, PAIRINGS_FILE, REPORTS_FILE, BLOCKED_FILE, VIP_FILE]:
    if not os.path.exists(file):
        with open(file, "w") as f:
            json.dump({}, f)

def load_json(path):
    with open(path) as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    users = load_json(USERS_FILE)
    if user_id not in users:
        users[user_id] = {
            "username": update.effective_user.username or "-",
            "vip": False,
            "paired_with": None
        }
        save_json(USERS_FILE, users)

    keyboard = [
        [InlineKeyboardButton("Cari Pasangan 🔍", callback_data="find")],
        [InlineKeyboardButton("Skip ⏭", callback_data="skip")],
        [InlineKeyboardButton("Rematch ♻️", callback_data="rematch")],
        [InlineKeyboardButton("Profil 🧑", callback_data="profile")],
        [InlineKeyboardButton("Laporkan 🚨", callback_data="report")],
        [InlineKeyboardButton("Donasi ❤️", callback_data="donate")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Selamat datang di bot pairing anonim kota!", reply_markup=reply_markup)

async def donate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    contact = os.getenv("DONATION_CONTACT")
    vip_price = os.getenv("VIP_PRICE")
    unblock_price = os.getenv("UNBLOCK_PRICE")
    text = f"Untuk menjadi VIP (akses rematch pasangan sebelumnya): Rp{vip_price}\n"
    text += f"Biaya membuka blokir oleh admin: Rp{unblock_price}\n"
    text += f"Hubungi admin untuk donasi: {contact}"
    await query.edit_message_text(text)

# Handlers pairing, skip, rematch, report, VIP, dsb akan ditambahkan berikutnya...

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(donate, pattern="^donate$"))
    # Tambahkan handler lain seperti pairing, rematch, dsb nanti di sini

    print("Bot berjalan...")
    app.run_polling()
