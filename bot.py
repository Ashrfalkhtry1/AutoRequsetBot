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
@app.on_chat_join_request(filters.group | filters.channel)
async def approve(_, m: Message):
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


@app.on_message(filters.private & filters.command("start"))
async def op(_, m: Message):
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

@app.on_callback_query(filters.regex("add_bot_to_channel"))
async def add_bot_to_channel_callback(_, cb: CallbackQuery):
    try:
        user_chats = await app.get_dialogs()
        channels = [
            chat for chat in user_chats
            if chat.chat.type == enums.ChatType.CHANNEL
        ]
        admin_channels = []
        for chat in channels:
            try:
                chat_member = await app.get_chat_member(chat.chat.id, cb.from_user.id)
                if chat_member.status in [enums.ChatMemberStatus.ADMIN, enums.ChatMemberStatus.CREATOR]:
                    admin_channels.append(chat)
            except Exception as e:
                continue

        if not admin_channels:
            await cb.answer("لم يتم العثور على قنوات مرتبطة بحسابك أو أنت لست مشرفًا في أي قناة.", show_alert=True)
            return

        buttons = [
            [InlineKeyboardButton(chat.chat.title, callback_data=f"select_channel_{chat.chat.id}")]
            for chat in admin_channels
        ]
        buttons.append([InlineKeyboardButton("رجوع", callback_data="go_back")])

        keyboard = InlineKeyboardMarkup(buttons)
        await cb.message.edit_text(
            "اختر القناة التي تريد إضافة البوت إليها:",
            reply_markup=keyboard
        )

    except Exception as e:
        print(f"Error: {e}")
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


@app.on_callback_query(filters.regex("channel_settings"))
async def channel_settings_callback(_, cb: CallbackQuery):
    channel_id = int(cb.data.split("_")[-1])
    try:
        chat = await app.get_chat(channel_id)
        keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("خزن الطلبات: مفعل", callback_data=f"toggle_store_{channel_id}")],
                [InlineKeyboardButton("قبول كل الطلبات المعلقة", callback_data=f"accept_all_{channel_id}")],
                [InlineKeyboardButton("تحديث المعلومات", callback_data=f"refresh_info_{channel_id}")],
                [InlineKeyboardButton("ازالة من البوت", callback_data=f"remove_channel_{channel_id}")],
                [InlineKeyboardButton("رجوع", callback_data=f"my_channels")]
            ]
        )
        await cb.message.edit_text(
            f"""هذه الاعدادات الخاصة بك

الاسم: {chat.title}
الايدي: {chat.id}
الرابط الخاص: {chat.invite_link}
خزن الطلبات: يخزن الطلبات لقبولها في وقت لاحق بموافقتك
الطلبات المعلقة: لا يوجد طلبات حاليا
""",
            reply_markup=keyboard
        )
    except Exception as e:
        print(e)
        await cb.answer("حدث خطأ أثناء جلب معلومات القناة.", show_alert=True)

@app.on_message(filters.command("users") & filters.user(cfg.SUDO))
async def dbtool(_, m: Message):
    xx = all_users()
    x = all_groups()
    tot = int(xx + x)
    await m.reply_text(text=f"Chats Stats Users: {xx} Groups: {x} Total: {tot}")

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

logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
