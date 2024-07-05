from pyrogram.enums import ParseMode
from subedit import bot
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from subedit.database.database import getLastMessageID, updateLastIndexAndMessageID
from subedit.helpers.Filters.custom_filters import CallbackButtonDataFilter
from subedit.plugins.editor.sub_editor import updateEdit
import asyncio


@bot.on_callback_query(CallbackButtonDataFilter("EDT__TEXT"))
async def editLine(_, query):
    # print(f"Data = {query.data}")
    instruction_msg = await bot.send_message(
        chat_id=query.from_user.id, text="Send the edited text."
    )
    sub_id = query.data.split("|")[1]
    next_index = int(query.data.split("|")[2])
    msg_id = await editorHandler(sub_id, next_index, query.from_user.id)
    await instruction_msg.delete()


async def editorHandler(subtitle_id, index, user_id):
    try:
        response = await bot.listen.Message(
            filters.text, filters.user(user_id), timeout=300
        )
    except asyncio.TimeoutError:
        error_msg = await bot.send_message(
            chat_id=user_id, text=f"Time out! Press **📝 Edit Text** button to restart."
        )
        return error_msg.id
    if response:
        edited_text = response.text
        updated_subtitle = await updateEdit(subtitle_id, index, edited_text)
        index = updated_subtitle["index"]
        start_time = updated_subtitle["start_time"]
        end_time = updated_subtitle["end_time"]
        timecode = f"{start_time} --> {end_time}"
        subtitle = updated_subtitle["original"]
        edited_line = updated_subtitle["edited"]
        if edited_line is None:
            content = f"**{index}**\n__{timecode}__\n\n`{subtitle}`"

        else:
            content = f"**{index}**\n__{timecode}__\n\n__Original__\n`{subtitle}`\n\n__Edited__\n`{edited_line}`"
        message_id = await getLastMessageID(subtitle_id)
        await bot.edit_message_text(
            chat_id=user_id,
            message_id=message_id,
            text=content,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "📝 Edit Text",
                            callback_data=f"EDT__TEXT|{subtitle_id}|{index}",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "🔗 Merge",
                            callback_data=f"{'MERGE_LINE' if index > 1 else 'MERGE'}|{subtitle_id}|{index}",
                        ),
                        InlineKeyboardButton(
                            "💠 Menu", callback_data=f"MAIN_MENU|{subtitle_id}|{index}",
                        ),
                        InlineKeyboardButton(
                            "✂️ Split", callback_data=f"SPLIT_LINE|{subtitle_id}|{index}"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            "➕ Add Line",
                            callback_data=f"ADD_NEW_LINE|{subtitle_id}|{index}",
                        ),
                        InlineKeyboardButton(
                            text="🎨 Formatter",
                            web_app=WebAppInfo(
                                url="https://anzilr.github.io/TextFormatter/"
                            ),
                        ),
                        InlineKeyboardButton(
                            "⏲️ Adjust Time",
                            callback_data=f"ADJUST_TIME_LINE|{subtitle_id}|{index}",
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            "⏪ Prev",
                            callback_data=f"{'PREV_LINE' if index > 1 else 'PREV'}|{subtitle_id}|{index - 1}",
                        ),
                        InlineKeyboardButton(
                            "🗑️ Delete", callback_data=f"DELETE_LINE|{subtitle_id}|{index}"
                        ),
                        InlineKeyboardButton(
                            "Next ⏩",
                            callback_data=f"NEXT_LINE|{subtitle_id}|{index + 1}",
                        ),
                    ],
                ]
            ),
        )
        await response.delete()
    # await asyncio.sleep(1)
    await bot.listen.Cancel(filters.user(user_id))
    return None
    # await asyncio.sleep(1)
    # await editorHandler(subtitle_id, index, user_id)
