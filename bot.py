import json, os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from yt_dlp import YoutubeDL

TOKEN = os.environ.get('TOKEN')
ADMIN_ID = int(os.environ.get('ADMIN_ID', 8544706424))
DB_FILE = 'bot_db.json'

def load_db():
    if not os.path.exists(DB_FILE):
        return {"commands": {}, "files": {}}
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

db = load_db()

def is_admin(update: Update):
    return update.effective_user.id == ADMIN_ID

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.message.reply_text('البوت خاص بالوحش كنج ⛔')
        return
    await update.message.reply_text('هلا بالوحش كنج 🔥\nالبوت شغال 24 ساعة\n\n/addcmd لاضافة أمر\n/delcmd لحذف أمر\n/list عرض كل الأوامر')

async def add_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update): return
    try:
        _, data = update.message.text.split(' ', 1)
        cmd, reply = data.split('|', 1)
        db["commands"][cmd.strip()] = reply.strip()
        save_db(db)
        await update.message.reply_text(f'✅ تم اضافة الأمر /{cmd.strip()}')
    except:
        await update.message.reply_text('الاستخدام:\n/addcmd اسم_الامر | الرد حقك')

async def del_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update): return
    try:
        cmd = context.args[0]
        if cmd in db["commands"]:
            del db["commands"][cmd]
            save_db(db)
            await update.message.reply_text(f'🗑️ تم حذف /{cmd}')
        else:
            await update.message.reply_text('الأمر مش موجود')
    except:
        await update.message.reply_text('الاستخدام: /delcmd اسم_الامر')

async def list_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update): return
    if not db["commands"]:
        await update.message.reply_text('مافي أوامر مضافة')
        return
    msg = "📋 الأوامر الحالية:\n"
    for cmd in db["commands"]: msg += f"/{cmd}\n"
    await update.message.reply_text(msg)

async def handle_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text.startswith('/'):
        cmd = text[1:].split(' ')[0]
        if cmd in db["commands"]:
            await update.message.reply_text(db["commands"][cmd])
            return
    if 'tiktok.com' in text or 'youtube.com' in text or 'youtu.be' in text:
        if not is_admin(update):
            await update.message.reply_text('البوت خاص ⛔')
            return
        msg = await update.message.reply_text('⏳ جاري التحميل...')
        options = {'format': 'best[ext=mp4]', 'outtmpl': 'temp.mp4', 'quiet': True}
        try:
            with YoutubeDL(options) as ydl:
                ydl.download([text])
            await update.message.reply_document(document=open('temp.mp4', 'rb'), caption='✅ تم يا كنج')
            os.remove('temp.mp4')
            await msg.delete()
        except:
            await msg.edit_text('❌ فشل التحميل')

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("addcmd", add_cmd))
app.add_handler(CommandHandler("delcmd", del_cmd))
app.add_handler(CommandHandler("list", list_cmd))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_all))
app.add_handler(MessageHandler(filters.COMMAND, handle_all))

print("بوت الوحش كنج شغال 24/7...")
app.run_polling()
