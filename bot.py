from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pyrogram.errors import FloodWait, UserNotParticipant, PeerIdInvalid
from database import add_channel, add_group, get_user_channels, get_user_groups, remove_channel, remove_group
from configs import cfg
import logging

# إعدادات البوت
app = Client(
    "auto_approve_bot",
    api_id=cfg.API_ID,
    api_hash=cfg.API_HASH,
    bot_token=cfg.BOT_TOKEN
)

# إعداد تسجيل الأخطاء
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# معالجة طلبات الانضمام التلقائية
@app.on_chat_join_request(filters.group | filters.channel)
async def auto_approve(_, m: Message):
    chat = m.chat
    user = m.from_user
    try:
        if chat.type == enums.ChatType.CHANNEL:
            add_channel(chat.id, user.id)
        elif chat.type == enums.ChatType.GROUP or chat.type == enums.ChatType.SUPERGROUP:
            add_group(chat.id, user.id)
        await app.approve_chat_join_request(chat.id, user.id)
        await app.send_message(user.id, f"تم قبول طلب انضمامك إلى {chat.title} بنجاح! 🎉")
    except Exception as e:
        logger.error(f"Error approving join request: {e}")

# أمر /start
@app.on_message(filters.private & filters.command("start"))
async def start(_, m: Message):
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("اضافة قناة", callback_data="add_channel")],
            [InlineKeyboardButton("اضافة جروب", callback_data="add_group")],
            [InlineKeyboardButton("قنواتي وجروباتي", callback_data="my_channels_groups")],
            [InlineKeyboardButton("انضمام الى قناة", url="https://t.me/your_channel_link")]
        ]
    )
    await m.reply_text(
        "مرحباً! أنا بوت قبول طلبات الانضمام التلقائي. يمكنك إضافة قنوات أو مجموعات لي لإدارة طلبات الانضمام تلقائياً.",
        reply_markup=keyboard
    )

# معالجة الأزرار
@app.on_callback_query(filters.regex("add_channel"))
async def add_channel_callback(_, cb: CallbackQuery):
    await cb.message.edit_text(
        "لإضافة قناة، قم برفع البوت كمسؤول في القناة ثم أرسل معرف القناة أو رابطها هنا.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("رجوع", callback_data="go_back")]])
    )

@app.on_callback_query(filters.regex("add_group"))
async def add_group_callback(_, cb: CallbackQuery):
    await cb.message.edit_text(
        "لإضافة مجموعة، قم برفع البوت كمسؤول في المجموعة ثم أرسل معرف المجموعة أو رابطها هنا.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("رجوع", callback_data="go_back")]])
    )

@app.on_callback_query(filters.regex("my_channels_groups"))
async def my_channels_groups_callback(_, cb: CallbackQuery):
    user_id = cb.from_user.id
    channels = get_user_channels(user_id)
    groups = get_user_groups(user_id)

    if not channels and not groups:
        await cb.message.edit_text("لم تقم بإضافة أي قنوات أو مجموعات بعد.")
        return

    text = "قنواتك:\n"
    for channel in channels:
        text += f"- {channel}\n"

    text += "\nمجموعاتك:\n"
    for group in groups:
        text += f"- {group}\n"

    await cb.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("رجوع", callback_data="go_back")]])
    )

@app.on_callback_query(filters.regex("go_back"))
async def go_back_callback(_, cb: CallbackQuery):
    await start(_, cb.message)

# معالجة الرسائل النصية لإضافة القنوات أو المجموعات
@app.on_message(filters.private & filters.text)
async def handle_text(_, m: Message):
    user_id = m.from_user.id
    text = m.text

    if text.startswith("@"):
        try:
            chat = await app.get_chat(text)
            if chat.type == enums.ChatType.CHANNEL:
                add_channel(chat.id, user_id)
                await m.reply_text(f"تمت إضافة القناة {chat.title} بنجاح! ✅")
            elif chat.type == enums.ChatType.GROUP or chat.type == enums.ChatType.SUPERGROUP:
                add_group(chat.id, user_id)
                await m.reply_text(f"تمت إضافة المجموعة {chat.title} بنجاح! ✅")
            else:
                await m.reply_text("الرجاء إرسال معرف قناة أو مجموعة صالح.")
        except Exception as e:
            await m.reply_text(f"حدث خطأ: {e}")
    else:
        await m.reply_text("الرجاء إرسال معرف قناة أو مجموعة يبدأ ب @.")

# تشغيل البوت
print("Bot is running!")
app.run()
