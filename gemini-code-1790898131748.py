import os
import re
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")

async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        if member.id == context.bot.id:
            continue
        welcome_text = (
            f"ሰላም {member.mention_html()}! 👋\n"
            f"እንኳን ወደ **{update.effective_chat.title}** ግሩፕ በደህና መጣህ/ሽ።"
        )
        await update.message.reply_html(welcome_text)

async def filter_spam_and_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    text = message.text or message.caption or ""
    link_pattern = r"(https?://[^\s]+|www\.[^\s]+|t\.me/[^\s]+|@[a-zA-Z0-9_]+)"
    
    if re.search(link_pattern, text):
        try:
            await message.delete()
            await message.chat.send_message(
                f"⚠️ {message.from_user.mention_html()}፡ በዚህ ግሩፕ ውስጥ ሊንክ ወይም ስፓም መላክ የተከለከለ ነው!"
            )
        except Exception as e:
            print(f"ስህተት፦ {e}")

def main():
    if not TOKEN:
        print("BOT_TOKEN አልተገኘም።")
        return

    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, filter_spam_and_links))

    print("ቦቱ ስራ ጀምሯል...")
    app.run_polling()

if __name__ == "__main__":
    main()