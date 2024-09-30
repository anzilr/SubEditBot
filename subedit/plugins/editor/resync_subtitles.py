import pysrt
from subedit import bot
from subedit.helpers.Filters.custom_filters import CallbackButtonDataFilter
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply
from pyrogram import filters
from subedit.database.database import (
    getSubtitleArray,
    UpdateSubtitleArray, checkCollabMemberBlacklist, checkCollabMember, getLastIndexAndMessageIDCollabStatus,
)

user_db = {}


@bot.on_callback_query(CallbackButtonDataFilter("RESYNC_SUB"))
async def resyncSubMenu(_, query):
    message_id = query.message.id
    subtitle_id = query.data.split("|")[1]
    indexx, messagee_id, collab_status = await getLastIndexAndMessageIDCollabStatus(subtitle_id)
    if collab_status:
        if not await checkCollabMember(subtitle_id, query.from_user.id):
            await query.answer("⛔️️ You are not authorized to edit this subtitle.", show_alert=True)
            return
        if await checkCollabMemberBlacklist(subtitle_id, query.from_user.id):
            await query.answer("⛔️️️ You are on the blacklist for this subtitle.", show_alert=True)
            return
    await bot.edit_message_text(
        chat_id=query.from_user.id,
        message_id=message_id,
        text="""You can adjust the timing of the subtitle file here.\n<b>How to use?</b>\n\n
             • If you want the subtitle to appear <i>10 seconds </i>earlier, reply <i>-10</i> to this message.\n
             • If you want the subtitle to appear <i>10 seconds </i>later, reply <i>10</i> to this message.""",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="❎ Cancel",
                        callback_data=f"MAIN_MENU|{subtitle_id}",
                    )
                ]
            ]
        ),
    )
    await bot.send_message(
        text="Send the time in seconds",
        chat_id=query.from_user.id,
        reply_to_message_id=message_id,
        reply_markup=ForceReply(placeholder="Time in seconds")
    )
    user_db[query.from_user.id] = {
        "message_id": message_id,
        "subtitle_id": subtitle_id
    }


@bot.on_message(filters.reply)
async def resyncSub(_, message):
    await bot.delete_messages(
        chat_id=message.from_user.id,
        message_ids=message.reply_to_message_id,
    )
    timecode = int(message.text)
    # print(message)
    message_id = user_db[message.from_user.id]["message_id"]
    subtitle_id = user_db[message.from_user.id]["subtitle_id"]
    await bot.edit_message_text(
        chat_id=message.from_user.id,
        message_id=message_id,
        text=f"Re-syncing subtitles, please wait ⏳..."
    )
    subtitles = await getSubtitleArray(subtitle_id)
    srt_items = []
    for subtitle in subtitles:
        start_time = pysrt.SubRipTime.from_string(subtitle["start_time"])
        end_time = pysrt.SubRipTime.from_string(subtitle["end_time"])
        original_text = subtitle["original"]
        edited_text = subtitle["edited"]

        # Create SubRipItem but delay appending to list
        srt_item = pysrt.SubRipItem(
            index=subtitle["index"],
            start=start_time,
            end=end_time,
            text=(
                original_text
                if edited_text is None
                else f"{original_text}||{edited_text}"
            ),
        )
        srt_items.append(srt_item)
    srt_file = pysrt.SubRipFile(items=srt_items)
    srt_file.shift(seconds=timecode)
    subtitle_data = []
    for sub in srt_file:
        try:
            original, edited = sub.text.split("||")
        except ValueError:
            original = sub.text
            edited = None
        subtitle_entry = {
            "index": sub.index,
            "start_time": str(sub.start),
            "end_time": str(sub.end),
            "original": original,
            "edited": edited,
        }
        subtitle_data.append(subtitle_entry)

    await UpdateSubtitleArray(subtitle_id, subtitle_data)
    await bot.delete_messages(
        chat_id=message.from_user.id,
        message_ids=message.id
    )
    await bot.edit_message_text(
        chat_id=message.from_user.id,
        message_id=message_id,
        text=f"Successfully re-synced the subtitle",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "🔭 Explore", switch_inline_query_current_chat=subtitle_id
                    ),
                    InlineKeyboardButton(
                        "Edit", callback_data=f"EDIT_SUB|{subtitle_id}"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "📦 Compile", callback_data=f"COMPILE_SUB|{subtitle_id}"
                    ),
                    InlineKeyboardButton(
                        "🗑️ Delete", callback_data=f"DELETE_SUB|{subtitle_id}"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "♻️ Re-sync", callback_data=f"RESYNC_SUB|{subtitle_id}"
                    )
                ]
            ]
        ),
    )
    if message.from_user.id in user_db:
        del user_db[message.from_user.id]
