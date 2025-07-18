import logging
import os
import asyncio
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# In-memory storage
users = {}
pairs = {}
reports = []
rematch_queue = {}

logging.basicConfig(level=logging.INFO)

# --- Bot Commands ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    users[uid] = {
        "name": update.effective_user.first_name,
        "age": None,
        "gender": None,
        "city": None,
        "status": "idle"
    }
    await update.message.reply_text("Halo! Ketik /profil untuk isi profilmu.")

async def profil(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Masukkan umurmu:")
    return 1

async def set_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    users[uid]["age"] = update.message.text
    await update.message.reply_text("Gender? (cowok/cewek)")
    return 2

async def set_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    users[uid]["gender"] = update.message.text
    await update.message.reply_text("Kota kamu?")
    return 3

async def set_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    users[uid]["city"] = update.message.text.lower()
    await update.message.reply_text("Profil selesai. Gunakan /cari untuk mulai cari pasangan.")
    return ConversationHandler.END

async def cari(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user = users.get(uid)
    if not user or not all([user["age"], user["gender"], user["city"]]):
        await update.message.reply_text("Lengkapi profil dulu dengan /profil")
        return

    user["status"] = "searching"
    for other_id, other in users.items():
        if other_id != uid and other["status"] == "searching" and other["city"] == user["city"]:
            users[uid]["status"] = "paired"
            users[other_id]["status"] = "paired"
            pairs[uid] = other_id
            pairs[other_id] = uid
            await context.bot.send_message(uid, f"🎉 Terhubung dengan {other['name']} (umur {other['age']}, {other['gender']})")
            await context.bot.send_message(other_id, f"🎉 Terhubung dengan {user['name']} (umur {user['age']}, {user['gender']})")
            return
    await update.message.reply_text("Menunggu pasangan...")

async def kirim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid in pairs:
        partner_id = pairs[uid]
        await context.bot.send_message(partner_id, f"💬 {update.message.text}")
    else:
        await update.message.reply_text("Kamu belum terhubung.")

async def skip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid in pairs:
        pid = pairs.pop(uid)
        pairs.pop(pid, None)
        users[uid]["status"] = "idle"
        users[pid]["status"] = "idle"
        rematch_queue[uid] = pid
        await context.bot.send_message(uid, "❌ Kamu melewati pasanganmu.")
        await context.bot.send_message(pid, "❌ Pasanganmu meninggalkan chat.")
    else:
        await update.message.reply_text("Kamu tidak sedang terhubung.")

async def rematch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid in rematch_queue:
        pid = rematch_queue.pop(uid)
        users[uid]["status"] = "paired"
        users[pid]["status"] = "paired"
        pairs[uid] = pid
        pairs[pid] = uid
        await context.bot.send_message(uid, "🔁 Kamu kembali terhubung.")
        await context.bot.send_message(pid, "🔁 Pasanganmu ingin terhubung kembali.")
    else:
        await update.message.reply_text("Tidak ada pasangan yang bisa dirematch.")

async def donasi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🙏 Dukung bot ini via Telegram: @iniiikan")

async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid in pairs:
        target = pairs[uid]
        reports.append((uid, target))
        await update.message.reply_text("🚨 Pasangan telah dilaporkan ke admin.")
    else:
        await update.message.reply_text("Tidak ada pasangan untuk dilaporkan.")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    msg = update.message.text.replace("/broadcast ", "")
    for uid in users:
        try:
            await context.bot.send_message(uid, f"[📢 Admin]: {msg}")
        except:
            continue
    await update.message.reply_text("✅ Broadcast terkirim.")

# --- App Setup ---

app = ApplicationBuilder().token(TOKEN).build()

conv_handler = ConversationHandler(
    entry_points=[CommandHandler("profil", profil)],
    states={
        1: [MessageHandler(filters.TEXT, set_age)],
        2: [MessageHandler(filters.TEXT, set_gender)],
        3: [MessageHandler(filters.TEXT, set_city)],
    },
    fallbacks=[],
)

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("cari", cari))
app.add_handler(CommandHandler("skip", skip))
app.add_handler(CommandHandler("rematch", rematch))
app.add_handler(CommandHandler("donasi", donasi))
app.add_handler(CommandHandler("report", report))
app.add_handler(CommandHandler("broadcast", broadcast))
app.add_handler(conv_handler)
app.add_handler(MessageHandler(filters.TEXT, kirim))

async def main():
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await app.updater.idle()

if _name_ == "_main_":
    asyncio.run(main())
