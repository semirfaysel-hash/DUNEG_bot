import os
import re
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")

# የተጠቃሚዎችን Add ያደረጉትን ሰው ብዛት ለመያዝ
user_add_counts = {}

REQUIRED_ADD_COUNT = 30

async def handle_new_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        if member.id == context.bot.id:
            continue
        
        # አዲስ ሰው ሲገባ የሚላክ ሰላምታ እና መመሪያ
        welcome_text = (
            f"ሰላም {member.mention_html()}! 👋\n\n"
            f"እንኳን ወደ **{update.effective_chat.title}** ግሩፕ በደህና መጣህ/ሽ።\n\n"
            f"⚠️ **ማሳሰቢያ፦** በግሩፑ ውስጥ ጽሁፍ ለመጻፍና ለመወያየት በመጀመሪያ **{REQUIRED_ADD_COUNT} ሰዎችን Add (አድ)** ማድረግ አለብህ/ሽ!"
        )
        await update.message.reply_html(welcome_text)

async def check_member_permissions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    user = message.from_user
    
    # ቦት ወይም አድሚን ከሆነ ምንም አይከለከልም
    if user.is_bot:
        return

    chat_member = await context.bot.get_chat_member(message.chat_id, user.id)
    if chat_member.status in ['creator', 'administrator']:
        return

    # አባሉ አድ ያደረገውን ሰው ብዛት ማረጋገጥ
    added_count = user_add_counts.get(user.id, 0)

    # ሰው አድ ከተደረገ ቁጥሩን መጨመር
    if message.new_chat_members:
        # አድ የሚያደርገው ሰው
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

    # 30 ሰው አድ ካላደረገ መልእክቱን ማጥፋት
    if added_count < REQUIRED_ADD_COUNT:
        try:
            await message.delete()
            remaining = REQUIRED_ADD_COUNT - added_count
            warning_msg = await message.chat.send_message(
                f"⚠️ {user.mention_html()}፡ በግሩፑ ውስጥ መጻፍ የምትችለው/ው **{REQUIRED_ADD_COUNT} ሰዎችን Add ስታደርግ/ጊ** ብቻ ነው።\n"
                f"እስካሁን ያደረግኸው/ሽው፦ **{added_count}** | የሚቀረህ/ሽ፦ **{remaining}**"
            )
        except Exception as e:
            print(f"ስህተት፦ {e}")

def main():
    if not TOKEN:
        print("BOT_TOKEN አልተገኘም።")
        return

    app = Application.builder().token(TOKEN).build()
    
    # አዲስ አባላት ሲገቡ
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, handle_new_members))
    
    # መልእክት ሲጻፍ አድ ማድረጋቸውን ማረጋገጥ
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, check_member_permissions))

    print("ቦቱ ስራ ጀምሯል...")
    app.run_polling()

if __name__ == "__main__":
    main()
