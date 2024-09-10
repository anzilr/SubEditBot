from pyrogram.enums import ParseMode

from subedit import bot
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from subedit.helpers.Filters.custom_filters import CallbackButtonDataFilter
from subedit.database.database import getLastIndexAndMessageID, updateLastMessageID
from subedit.plugins.editor.sub_editor import fetchLine


@bot.on_callback_query(CallbackButtonDataFilter("EDIT_SUB"))
async def editSubHandler(_, query):
    sub_id = query.data.split("|")[1]
    index, last_message_id = await getLastIndexAndMessageID(sub_id)
    if index is None:
        index = 1
    line = await fetchLine(sub_id, index)
    index = line["index"]
    start_time = line["start_time"]
    end_time = line["end_time"]
    timecode = f"{start_time} --> {end_time}"
    subtitle = line["original"]
    edited_line = line["edited"]
    if edited_line is None:
        content = f"**{index}**\n__{timecode}__\n\n`{subtitle}`"

    else:
        content = f"**{index}**\n__{timecode}__\n\n__Original__\n`{subtitle}`\n\n__Edited__\n`{edited_line}`"
    msg = await bot.send_message(
        chat_id=query.from_user.id,
        text=content,
        parse_mode=ParseMode.MARKDOWN,
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
                        "👨🏽‍💻 Translate", callback_data=f"TRANSLATE|{sub_id}|{index}"
                    ),
                    InlineKeyboardButton(
                        text="📺 Player",
                        web_app=WebAppInfo(
                            url=f"https://eblayer-anzilr9398-jh1n7zan.leapcell.dev/player/{sub_id}/{index}/"
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
        ),
    )
    await updateLastMessageID(sub_id, msg.id)
    # await sharedDB.createSharedDB(query.from_user.id, sub_id, msg.id, index)
    # await editorHandler(sub_id, index, query.from_user.id)
