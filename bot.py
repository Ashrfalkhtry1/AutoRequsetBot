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

# Main process

@app.on_chat_join_request(filters.group | filters.channel)
async def approve(_, m : Message):
    op = m.chat
    kk = m.from_user
    try:
        add_group(m.chat.id)
        await app.approve_chat_join_request(op.id, kk.id)
        await app.send_message(kk.id, f"""مرحباً {m.from_user.mention} 🐾❤️👋

✨ **بوت إدارة طلبات الانضمام** ✨  
هذا البوت يتيح لك قبول طلبات الانضمام الخاصة بالقنوات والكروبات ✅  
يمكنك:
- قبول الطلبات مباشرة بشكل تلقائي.  
- تخزينها لقبولها لاحقاً بضغطة زر 📩  

📢 **قناة البوت:** [@looniaa1](https://t.me/looniaa1)  
👨‍💻 **صانع البوتات:** [@dev_ashrf](https://t.me/dev_ashrf)  
""")
        add_user(kk.id)
    except errors.PeerIdInvalid as e:
        print("user isn't start bot(means group)")
    except Exception as err:
        print(str(err))    

# Start

@app.on_message(filters.private & filters.command("start"))
async def op(_, m :Message):
    try:
        await app.get_chat_member(cfg.CHID, m.from_user.id)
    except:
        try:
            invite_link = await app.create_chat_invite_link(int(cfg.CHID))
        except:
            await m.reply("Make Sure I Am Admin In Your Channel")
            return 
        key = InlineKeyboardMarkup(
            [[
                InlineKeyboardButton("Join Update Channel", url=invite_link.invite_link),
                InlineKeyboardButton("Check Again", callback_data="chk")
            ]]
        ) 
        await m.reply_text("Access Denied! Join My Update Channel To Use Me.", reply_markup=key)
        return 
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("اضافة قناة", callback_data="add_channel"),
                InlineKeyboardButton("اضافة كروب", callback_data="add_group")
            ],
            [
                InlineKeyboardButton("قنواتي وكروباتي", callback_data="my_channels")
            ],
            [
                InlineKeyboardButton("انضمام الى القناة", url="https://t.me/+rfquoCO_seszYzRk")
            ]
        ]
    )
    add_user(m.from_user.id)
    await m.reply_photo(
    "https://ibb.co/vhW9ntn", 
    caption=f"""مرحباً {m.from_user.mention} 🐾❤️👋

✨ **بوت إدارة طلبات الانضمام** ✨  
هذا البوت يتيح لك قبول طلبات الانضمام الخاصة بالقنوات والكروبات ✅  
يمكنك:
- قبول الطلبات مباشرة بشكل تلقائي.  
- تخزينها لقبولها لاحقاً بضغطة زر 📩  

📢 **قناة البوت:** [@looniaa1](https://t.me/looniaa1)  
👨‍💻 **صانع البوتات:** [@dev_ashrf](https://t.me/dev_ashrf)  
""",
    reply_markup=keyboard
    )

# Callback handlers
@app.on_callback_query(filters.regex("add_channel"))
async def add_channel_callback(_, cb: CallbackQuery):
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("إضافة البوت إلى القناة", callback_data="add_bot_to_channel"),
                InlineKeyboardButton("رجوع", callback_data="go_back")
            ]
        ]
    )
    await cb.message.edit_text(
        "ارفع البوت مشرف في قناتك\nثم ارسل توجيه من قناتك أو معرف القناة",
        reply_markup=keyboard
    )

# إعداد نظام تسجيل الأخطاء
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@app.on_callback_query(filters.regex("add_bot_to_channel"))
async def add_bot_to_channel_callback(_, cb: CallbackQuery):
    try:
        # استخدام async for للتكرار عبر الحوارات
        user_chats = [chat async for chat in app.get_dialogs()]
        
        # تصفية القنوات فقط
        channels = [
            chat for chat in user_chats
            if chat.chat.type in (enums.ChatType.CHANNEL, enums.ChatType.SUPERGROUP)
        ]

        if not channels:
            await cb.answer("لم يتم العثور على قنوات مرتبطة بحسابك.", show_alert=True)
            return

        # إنشاء أزرار للقنوات
        buttons = [
            [InlineKeyboardButton(chat.chat.title, callback_data=f"select_channel_{chat.chat.id}")]
            for chat in channels
        ]
        buttons.append([InlineKeyboardButton("رجوع", callback_data="add_channel")])

        keyboard = InlineKeyboardMarkup(buttons)
        
        # تحقق من النص الحالي للرسالة لتجنب التكرار
        if cb.message.text != "اختر القناة التي تريد إضافة البوت إليها:":
            await cb.message.edit_text(
                "اختر القناة التي تريد إضافة البوت إليها:",
                reply_markup=keyboard
            )
    except errors.FloodWait as e:
        logger.error(f"FloodWait: {e.value} ثانية.")
        await asyncio.sleep(e.value)
        await cb.answer("حدث تأخير أثناء جلب القنوات، يرجى المحاولة لاحقاً.", show_alert=True)
    except errors.RPCError as e:
        logger.error(f"RPC Error: {e}")
        await cb.answer("تحقق من إعدادات حسابك أو حاول مجددًا لاحقاً.", show_alert=True)
    except Exception as e:
        logger.error(f"Unexpected Error: {e}")
        await cb.answer("حدث خطأ أثناء جلب القنوات. تحقق من الصلاحيات وحاول مرة أخرى.", show_alert=True)


@app.on_callback_query(filters.regex("select_channel_"))
async def select_channel_callback(_, cb: CallbackQuery):
    channel_id = int(cb.data.split("_")[-1])
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Add bot as Admin", callback_data=f"add_admin_{channel_id}")],
            [InlineKeyboardButton("رجوع", callback_data="add_bot_to_channel")]
        ]
    )
    await cb.message.edit_text(
        f"قم برفع البوت مشرف في القناة {channel_id}.\nثم اختر الصلاحيات التي ستعطيها للبوت:",
        reply_markup=keyboard
    )

@app.on_callback_query(filters.regex("add_admin_"))
async def add_admin_callback(_, cb: CallbackQuery):
    channel_id = int(cb.data.split("_")[-1])
    try:
        # Simulate adding the bot as an admin
        await cb.answer("تم إضافة البوت كأدمن!", show_alert=True)
        await cb.message.edit_text(
            f"تم إضافة البوت كأدمن في القناة {channel_id}.\nالرجاء إرسال توجيه من قناتك أو معرف القناة لإتمام العملية."
        )
    except Exception as e:
        print(e)
        await cb.answer("حدث خطأ أثناء رفع البوت كأدمن.", show_alert=True)

@app.on_callback_query(filters.regex("go_back"))
async def go_back_callback(_, cb: CallbackQuery):
    await op(_, cb.message)

# Info

@app.on_message(filters.command("users") & filters.user(cfg.SUDO))
async def dbtool(_, m : Message):
    xx = all_users()
    x = all_groups()
    tot = int(xx + x)
    await m.reply_text(text=f"Chats Stats Users: {xx} Groups: {x} Total: {tot}")

# Broadcast

@app.on_message(filters.command("bcast") & filters.user(cfg.SUDO))
async def bcast(_, m: Message):
    allusers = users
    lel = await m.reply_text("Processing...")
    success = 0
    failed = 0
    deactivated = 0
    blocked = 0

    for usrs in allusers.find():
        try:
            userid = usrs["user_id"]
            if m.command[0] == "bcast":
                await m.reply_to_message.copy(int(userid))
            success += 1
        except FloodWait as ex:
            await asyncio.sleep(ex.value)
            if m.command[0] == "bcast":
                await m.reply_to_message.copy(int(userid))
        except errors.InputUserDeactivated:
            deactivated += 1
            remove_user(userid)
        except errors.UserIsBlocked:
            blocked += 1
        except Exception as e:
            print(e)
            failed += 1

    await lel.edit(f"Success: {success} Failed: {failed} Blocked: {blocked} Deactivated: {deactivated}")
print("Bot is running!")
app.run()
