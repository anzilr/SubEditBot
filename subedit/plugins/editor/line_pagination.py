from subedit import bot
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from subedit.database.database import getLastMessageID, updateLastIndexAndMessageID
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
    msg_id = await getLastMessageID(sub_id)
    line = await fetchLine(sub_id, index=next_index)
    index = line["index"]
    start_time = line["start_time"]
    end_time = line["end_time"]
    timecode = f"{start_time} --> {end_time}"
    subtitle = line["original"]
    edited_line = line["edited"]
    if edited_line is None:
        content = f"<b>{index}</b>\n<i>{timecode}</i>\n\n<code>{subtitle}</code>"

    else:
        content = f"<b>{index}</b>\n<i>{timecode}</i>\n\n<i>Original</i>\n<code>{subtitle}</code>\n\n<i>Edited</i>\n<code>{edited_line}</code>"
    msg = await bot.edit_message_text(
        chat_id=query.from_user.id,
        text=content,
        message_id=msg_id,
        reply_markup=InlineKeyboardMarkup(
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
        ),
    )
    await updateLastIndexAndMessageID(sub_id, index, msg.id)
    # await editorHandler(sub_id, index, query.from_user.id)
