from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pyrogram import filters, Client, errors, enums
from pyrogram.errors import UserNotParticipant
from pyrogram.errors.exceptions.flood_420 import FloodWait
from database import add_user, add_group, all_users, all_groups, users, remove_user
from configs import cfg
import random, asyncio
import logging

app = Client(
    "approver",
    api_id=cfg.API_ID,
    api_hash=cfg.API_HASH,
    bot_token=cfg.BOT_TOKEN
)
import logging
from telegram import Update, ChatInviteLink
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ChatJoinRequestHandler,
    ContextTypes,
)

# ------------------------------------------
# 1) ضبط اللوج
# ------------------------------------------
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ------------------------------------------
# 2) ضع التوكن الخاص ببوتك هنا
# ------------------------------------------


# ------------------------------------------
# 3) متغير لتخزين بيانات القنوات والمجموعات للمستخدمين في الذاكرة
#    البنية: {user_id: {"channels": [], "groups": []}}
# ------------------------------------------
user_data_store = {}

# ------------------------------------------
# 4) دالة لقبول طلب الانضمام تلقائي
# ------------------------------------------
async def join_request_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_join_request = update.chat_join_request
    user_id = chat_join_request.from_user.id
    chat_id = chat_join_request.chat.id

    # قبول طلب الانضمام
    await context.bot.approve_chat_join_request(chat_id=chat_id, user_id=user_id)

    # إرسال رسالة ترحيب في الخاص (إن أمكن)
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=f"مرحبًا {chat_join_request.from_user.first_name}!\n"
                 f"تم قبول طلب انضمامك في المجموعة/القناة بنجاح."
        )
    except Exception as e:
        logging.warning(f"تعذر إرسال رسالة خاصة للمستخدم {user_id}: {e}")

# ------------------------------------------
# 5) أوامر البوت
# ------------------------------------------

# --- أمر /start ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # تهيئة التخزين للمستخدم إن لم يكن موجودًا
    if user_id not in user_data_store:
        user_data_store[user_id] = {"channels": [], "groups": []}

    await update.message.reply_text(
        "أهلاً بك!\n"
        "استخدم الأوامر التالية:\n"
        "/addchannel - لإضافة قناة\n"
        "/addgroup - لإضافة مجموعة\n"
        "/mylist - لعرض القنوات والمجموعات لديك\n"
        "/joinchannel - للانضمام إلى قناة محددة"
    )

# --- أمر /addchannel ---
async def add_channel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # التأكد من وجود بارامتر (اسم قناة أو رابط)
    if not context.args:
        await update.message.reply_text("الرجاء كتابة اسم المستخدم الخاص بالقناة أو رابط القناة بعد الأمر.\nمثال: /addchannel @channel_username")
        return

    channel_link_or_username = context.args[0]

    # حفظ القناة في ذاكرة المستخدم
    if user_id not in user_data_store:
        user_data_store[user_id] = {"channels": [], "groups": []}

    user_data_store[user_id]["channels"].append(channel_link_or_username)

    await update.message.reply_text(
        f"تم إضافة القناة: {channel_link_or_username} إلى قائمتك بنجاح!"
    )

# --- أمر /addgroup ---
async def add_group_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # التأكد من وجود بارامتر (اسم مجموعة أو رابط)
    if not context.args:
        await update.message.reply_text("الرجاء كتابة رابط أو اسم مستخدم المجموعة بعد الأمر.\nمثال: /addgroup @my_private_group")
        return

    group_link_or_username = context.args[0]

    # حفظ المجموعة في ذاكرة المستخدم
    if user_id not in user_data_store:
        user_data_store[user_id] = {"channels": [], "groups": []}

    user_data_store[user_id]["groups"].append(group_link_or_username)

    await update.message.reply_text(
        f"تم إضافة المجموعة: {group_link_or_username} إلى قائمتك بنجاح!"
    )

# --- أمر /mylist ---
async def my_list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # التأكد من أن للمستخدم بيانات
    if user_id not in user_data_store:
        await update.message.reply_text("لا توجد أي بيانات محفوظة لديك.")
        return

    channels = user_data_store[user_id]["channels"]
    groups = user_data_store[user_id]["groups"]

    if not channels and not groups:
        await update.message.reply_text("قائمتك خالية من القنوات والمجموعات.")
        return

    msg = "قنواتك:\n" if channels else "لا توجد قنوات.\n"
    for ch in channels:
        msg += f"- {ch}\n"

    msg += "\nمجموعاتك:\n" if groups else "\nلا توجد مجموعات.\n"
    for gr in groups:
        msg += f"- {gr}\n"

    await update.message.reply_text(msg)

# --- أمر /joinchannel ---
async def join_channel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    هذا الأمر يرسل رابط الانضمام للقناة إن كان متاحًا.
    يجب أن يكون البوت أدمن في القناة حتى يستطيع إنشاء رابط دعوة.
    """
    if not context.args:
        await update.message.reply_text("الرجاء إدخال معرف القناة (username) بعد الأمر.\nمثال: /joinchannel @mychannel")
        return

    channel_username = context.args[0]

    try:
        # إنشاء رابط دعوة مؤقت (قابل للاستخدام مرة واحدة أو أكثر حسب الإعدادات)
        invite_link: ChatInviteLink = await context.bot.create_chat_invite_link(
            chat_id=channel_username,
            name="Temp Link",  # اسم وصفي للرابط (اختياري)
            creates_join_request=False,  # إذا True فسيكون 'طلب انضمام' وليس رابط دعوة مباشر
            member_limit=1,  # مثلاً رابط لشخص واحد
            expire_date=None  # يمكن تحديد وقت انتهاء
        )

        await update.message.reply_text(
            f"هذا هو رابط الدعوة لقناتك:\n{invite_link.invite_link}\n"
            f"يسمح بدخول مستخدم واحد فقط (حسب الإعدادات)."
        )
    except Exception as e:
        logging.error(f"حصل خطأ أثناء إنشاء رابط الدعوة: {e}")
        await update.message.reply_text(
            "تعذر إنشاء رابط دعوة. تأكد أن البوت أدمن في القناة ولديه الصلاحيات المناسبة."
        )

# ------------------------------------------
# 6) الدالة الرئيسية لتشغيل البوت
# ------------------------------------------
async def main():
    # إنشاء التطبيق (Application)
    application = ApplicationBuilder().token(cfg.BOT_TOKEN).build()

    # إضافة الهاندلر الخاص بطلبات الانضمام
    application.add_handler(ChatJoinRequestHandler(join_request_handler))

    # إضافة أوامر البوت
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("addchannel", add_channel_command))
    application.add_handler(CommandHandler("addgroup", add_group_command))
    application.add_handler(CommandHandler("mylist", my_list_command))
    application.add_handler(CommandHandler("joinchannel", join_channel_command))

    # تشغيل البوت (Polling)
    await application.run_polling()

# ------------------------------------------
# 7) تشغيل البوت
# ------------------------------------------
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
