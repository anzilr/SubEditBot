from subedit import bot
from subedit.helpers.Filters.custom_filters import (
    CallbackButtonDataFilter,
    UserStateFilter,
)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from subedit.database.database import (
    getLastMessageID,
    getSubtitleByIndex,
    updateNewTime,
    updateLastIndexAndMessageID,
)
from subedit.plugins.editor.line_pagination import paginateLine
from subedit.plugins.editor.sub_editor import fetchLine

user_state = {}


@bot.on_callback_query(CallbackButtonDataFilter("ADJUST_TIME_LINE"))
async def adjustTime(_, query):
    subtitle_id = query.data.split("|")[1]
    index = int(query.data.split("|")[2])
    message_id = await getLastMessageID(subtitle_id)
    await bot.edit_message_text(
        chat_id=query.from_user.id,
        text=f"Adjust the duration of current line.\n\n<i><b>Tip: Note the time codes of previous and next lines before adjust the time to avoid overlapping subtitles</b></i>.",
        message_id=message_id,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Adjust Time",
                        callback_data=f"ADJUST_LINE_TIME|{subtitle_id}|{index}",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="Cancel",
                        callback_data=f"CANCEL_TIME_ADJUST|{subtitle_id}|{index}",
                    )
                ],
            ]
        ),
    )


@bot.on_callback_query(CallbackButtonDataFilter("ADJUST_LINE_TIME"))
async def adjustLineTime(_, query):
    subtitle_id = query.data.split("|")[1]
    index = int(query.data.split("|")[2])
    message_id = await getLastMessageID(subtitle_id)
    subtitle = await getSubtitleByIndex(subtitle_id, index)
    user_state[query.from_user.id] = {
        "state": "edit_time",
        "index": index,
        "subtitle_id": subtitle_id,
        "subtitle": subtitle,
    }
    start_time = subtitle["start_time"]
    end_time = subtitle["end_time"]
    timecode = f"{start_time} > {end_time}"
    await bot.edit_message_text(
        chat_id=query.from_user.id,
        text=f"<i><b>Tip: Note the time codes of previous and next lines before adjust the time to avoid overlapping subtitles</b></i>.\n\nClick on the text below to copy and send the new time.\nFormat\n<i>Hour:Minutes:Seconds,Micro Seconds</i>\n<code>{timecode}</code>",
        message_id=message_id,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Cancel",
                        callback_data=f"CANCEL_TIME_ADJUST|{subtitle_id}|{index}",
                    )
                ]
            ]
        ),
    )


@bot.on_message(UserStateFilter(user_state))
async def inputNewTime(_, message):
    timecode = message.text
    start, end = timecode.split(" > ")
    subtitle_id = user_state[message.from_user.id]["subtitle_id"]
    index = user_state[message.from_user.id]["index"]
    subtitle = user_state[message.from_user.id]["subtitle"]
    subtitle["start_time"] = start
    subtitle["end_time"] = end
    await updateNewTime(subtitle_id, index, start, end)
    if message.from_user.id in user_state:
        del user_state[message.from_user.id]
    msg_id = await getLastMessageID(subtitle_id)
    line = await fetchLine(subtitle_id, index=index)
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
        chat_id=message.from_user.id,
        text=content,
        message_id=msg_id,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Edit Text", callback_data=f"EDT__TEXT|{subtitle_id}|{index}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "Merge",
                        callback_data=f"{'MERGE_LINE' if index > 1 else 'MERGE'}|{subtitle_id}|{index}",
                    ),
                    InlineKeyboardButton(
                        "Split", callback_data=f"SPLIT_LINE|{subtitle_id}|{index}"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "Add Line", callback_data=f"ADD_NEW_LINE|{subtitle_id}|{index}"
                    ),
                    InlineKeyboardButton(
                        text="Formatter",
                        web_app=WebAppInfo(
                            url="https://anzilr.github.io/TextFormatter/"
                        ),
                    ),
                    InlineKeyboardButton(
                        "Adjust Time",
                        callback_data=f"ADJUST_TIME_LINE|{subtitle_id}|{index}",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "<< Prev",
                        callback_data=f"{'PREV_LINE' if index > 1 else 'PREV'}|{subtitle_id}|{index - 1}",
                    ),
                    InlineKeyboardButton(
                        "Delete", callback_data=f"DELETE_LINE|{subtitle_id}|{index}"
                    ),
                    InlineKeyboardButton(
                        "Next >>", callback_data=f"NEXT_LINE|{subtitle_id}|{index + 1}"
                    ),
                ],
            ]
        ),
    )
    await updateLastIndexAndMessageID(subtitle_id, index, msg.id)
    await message.delete()


@bot.on_callback_query(CallbackButtonDataFilter("CANCEL_TIME_ADJUST"))
async def cancelTimeAdjust(_, query):
    if query.from_user.id in user_state:
        del user_state[query.from_user.id]
    await paginateLine(query)
