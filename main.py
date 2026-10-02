import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# Render Port እንዳያጣ Dummy Web Server ማዘጋጀት
web_app = Flask(__name__)

@web_app.route('/')
def health_check():
    return "Bot is running live!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host="0.0.0.0", port=port)

TOKEN = os.getenv("BOT_TOKEN")
user_add_counts = {}
REQUIRED_ADD_COUNT = 30

async def handle_new_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        if member.id == context.bot.id:
            continue
        
        welcome_text = (
            f"ሰላም {member.mention_html()}! 👋\n\n"
            f"እንኳን ወደ **{update.effective_chat.title}** ግሩፕ በደህና መጣህ/ሽ።\n\n"
            f"⚠️ **ማሳሰቢያ፦** በግሩፑ ውስጥ ጽሁፍ ለመጻፍና ለመወያየት በመጀመሪያ **{REQUIRED_ADD_COUNT} ሰዎችን Add (አድ)** ማድረግ አለብህ/ሽ!"
        )
        await update.message.reply_html(welcome_text)

async def check_member_permissions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    user = message.from_user
    
    if user.is_bot:
        return

    chat_member = await context.bot.get_chat_member(message.chat_id, user.id)
    if chat_member.status in ['creator', 'administrator']:
        return

    added_count = user_add_counts.get(user.id, 0)

    if message.new_chat_members:
        adder_id = user.id
        added_num = len(message.new_chat_members)
        user_add_counts[adder_id] = user_add_counts.get(adder_id, 0) + added_num
        
        current_total = user_add_counts[adder_id]
        if current_total < REQUIRED_ADD_COUNT:
            remaining = REQUIRED_ADD_COUNT - current_total
            await message.reply_html(
                f"👍 {user.mention_html()}፣ {added_num} ሰው አድ አድርገሃል/ሻል።\n"
                f"መልእክት ለመጻፍ ገና **{remaining} ሰው** ያንስሃል/ሻል።"
            )
        else:
            await message.reply_html(
                f"🎉 እንኳን ደስ አለህ/ሽ {user.mention_html()}! **{REQUIRED_ADD_COUNT}** ሰው አድ አድርገህ/ሽ ጨርሰሃል/ሻል። አሁን መወያየት ትችላለህ/ሽ!"
            )
        return

    if added_count < REQUIRED_ADD_COUNT:
        try:
            await message.delete()
            remaining = REQUIRED_ADD_COUNT - added_count
            await message.chat.send_message(
                f"⚠️ {user.mention_html()}፡ በግሩፑ ውስጥ መጻፍ የምትችለው/ው **{REQUIRED_ADD_COUNT} ሰዎችን Add ስታደርግ/ጊ** ብቻ ነው።\n"
                f"እስካሁን ያደረግኸው/ሽው፦ **{added_count}** | የሚቀረህ/ሽ፦ **{remaining}**"
            )
        except Exception as e:
            print(f"ስህተት፦ {e}")

def main():
    if not TOKEN:
        print("BOT_TOKEN አልተገኘም።")
        return

    # Flask ዌብ ሰርቨሩን ከበስተጀርባ ማስነሳት
    threading.Thread(target=run_flask, daemon=True).start()

    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, handle_new_members))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, check_member_permissions))

    print("ቦቱ ስራ ጀምሯል...")
    app.run_polling()

if __name__ == "__main__":
    main()
