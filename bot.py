from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pyrogram import filters, Client, errors, enums
from pyrogram.errors import UserNotParticipant
from pyrogram.errors.exceptions.flood_420 import FloodWait
from database import add_user, add_group, all_users, all_groups, users, remove_user
from configs import cfg
import random, asyncio

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
                InlineKeyboardButton("انضمام الى القناة", url="https://t.me/looniaa1")
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
    await cb.answer("خاصية إضافة القناة قيد التطوير!", show_alert=True)

@app.on_callback_query(filters.regex("add_group"))
async def add_group_callback(_, cb: CallbackQuery):
    await cb.answer("خاصية إضافة الكروب قيد التطوير!", show_alert=True)

@app.on_callback_query(filters.regex("my_channels"))
async def my_channels_callback(_, cb: CallbackQuery):
    await cb.answer("عرض قنواتك وكروباتك قيد التطوير!", show_alert=True)

# Info

@app.on_message(filters.command("users") & filters.user(cfg.SUDO))
async def dbtool(_, m : Message):
    xx = all_users()
    x = all_groups()
    tot = int(xx + x)
    await m.reply_text(text=f"Chats Stats Users: {xx} Groups: {x} Total: {tot}")

# Broadcast

@app.on_message(filters.command("bcast") & filters.user(cfg.SUDO))
async def bcast(_, m : Message):
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
