from subedit import bot
from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.errors.exceptions.bad_request_400 import MessageNotModified
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from subedit.database.database import getLastMessageID, updateLastIndexAndMessageID, checkCollabMember, \
    getLastIndexAndMessageIDCollabStatus, checkCollabMemberBlacklist
from subedit.helpers.Filters.custom_filters import CallbackButtonDataFilter
from subedit.plugins.editor.sub_editor import fetchLine


@bot.on_callback_query(CallbackButtonDataFilter("NEXT_LINE"))
async def nextLine(_, query):
    await paginateLine(query)


@bot.on_callback_query(CallbackButtonDataFilter("PREV_LINE"))
async def prevLine(_, query):
    await paginateLine(query)


async def paginateLine(query):
    print(query.data)
    try:
        await bot.listen.Cancel(filters.user(query.from_user.id))
    except Exception as e:
        pass
    sub_id = query.data.split("|")[1]
    next_index = int(query.data.split("|")[2])
    # msg_id = await getLastMessageID(sub_id)
    user_id = query.from_user.id
    index, msg_id, collab_status = await getLastIndexAndMessageIDCollabStatus(sub_id)
    if collab_status:
        if not await checkCollabMember(sub_id, user_id):
            await query.answer("⛔️️ You are not authorized to edit this subtitle.", show_alert=True)
            return
        if await checkCollabMemberBlacklist(sub_id, user_id):
            await query.answer("⛔️️️ You are on the blacklist for this subtitle.", show_alert=True)
            return
    line = await fetchLine(sub_id, index=next_index)
    try:
        index = line["index"]
    except TypeError:
        return await query.answer(
            "No more lines.", show_alert=True
        )
    start_time = line["start_time"]
    end_time = line["end_time"]
    timecode = f"{start_time} --> {end_time}"
    subtitle = line["original"]
    edited_line = line["edited"]
    if edited_line is None:
        content = f"**{index}**\n__{timecode}__\n\n`{subtitle}`"

    else:
        content = f"**{index}**\n__{timecode}__\n\n__Original__\n`{subtitle}`\n\n__Edited__\n`{edited_line}`"

    reply_markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "📝 Edit Text", callback_data=f"EDT__TEXT|{sub_id}|{index}"
                )
            ],
            [
                InlineKeyboardButton(
                    "🔗 Merge",
                    callback_data=f"{'MERGE_LINE' if index > 1 else 'MERGE'}|{sub_id}|{index}",
                ),
                InlineKeyboardButton(
                    "💠 Menu", callback_data=f"MAIN_MENU|{sub_id}|{index}",
                ),
                InlineKeyboardButton(
                    "✂️ Split", callback_data=f"SPLIT_LINE|{sub_id}|{index}"
                ),
            ],
            [
                InlineKeyboardButton(
                    "➕ Add Line", callback_data=f"ADD_NEW_LINE|{sub_id}|{index}"
                ),
                InlineKeyboardButton(
                    text="🎨 Formatter",
                    web_app=WebAppInfo(
                        url="https://anzilr.github.io/TextFormatter/"
                    ),
                ),
                InlineKeyboardButton(
                    "⏲️ Adjust Time",
                    callback_data=f"ADJUST_TIME_LINE|{sub_id}|{index}",
                ),
            ],
            [
                InlineKeyboardButton(
                    "👨🏽‍💻 Translate", callback_data=f"TRANSLATE|{sub_id}|{index}"
                ),
                InlineKeyboardButton(
                    text="📺 Player",
                    web_app=WebAppInfo(
                        url=f"https://eblayer-anzilr9398-jh1n7zan.leapcell.dev/player/{sub_id}/{index}"
                    ),
                ),
            ],
            [
                InlineKeyboardButton(
                    "⏪ Prev",
                    callback_data=f"{'PREV_LINE' if index > 1 else 'PREV'}|{sub_id}|{index - 1}",
                ),
                InlineKeyboardButton(
                    "🗑️ Delete", callback_data=f"DELETE_LINE|{sub_id}|{index}"
                ),
                InlineKeyboardButton(
                    "Next ⏩", callback_data=f"NEXT_LINE|{sub_id}|{index + 1}"
                ),
            ],
        ]
    )
    try:

        msg = await bot.edit_message_text(
            chat_id=query.from_user.id,
            text=content,
            message_id=msg_id,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    except MessageNotModified:
        msg = await bot.send_message(
            chat_id=query.from_user.id,
            text=content,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    await updateLastIndexAndMessageID(sub_id, index, msg.id)
    # await editorHandler(sub_id, index, query.from_user.id)
