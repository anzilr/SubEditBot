from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from subedit import bot
import pysrt
import asyncio
from subedit.plugins.editor.line_pagination import paginateLine
from subedit.helpers.Filters.custom_filters import CallbackButtonDataFilter
from subedit.database.database import getSubtitleArray, UpdateSubtitleArray, getLastMessageID, \
    getLastIndexAndMessageIDCollabStatus, checkCollabMember, checkCollabMemberBlacklist


@bot.on_callback_query(CallbackButtonDataFilter("DELETE_LINE"))
async def deleteLine(_, query):
    sub_id = query.data.split("|")[1]
    delete_index = int(query.data.split("|")[2])
    # message_id = await getLastMessageID(sub_id)
    indexx, message_id, collab_status = await getLastIndexAndMessageIDCollabStatus(sub_id)
    if collab_status:
        if not await checkCollabMember(sub_id, query.from_user.id):
            await query.answer("⛔️️ You are not authorized to edit this subtitle.", show_alert=True)
            return
        if await checkCollabMemberBlacklist(sub_id, query.from_user.id):
            await query.answer("⛔️️️ You are on the blacklist for this subtitle.", show_alert=True)
            return
    await bot.edit_message_text(
        chat_id=query.from_user.id,
        message_id=message_id,
        text=f"<i>Deleting Line {delete_index}</i>",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="🚮 OK",
                        callback_data=f"DELETE_CURRENT_LINE|{sub_id}|{delete_index}",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="❎ Cancel",
                        callback_data=f"CANCEL_DELETE_LINE|{sub_id}|{delete_index}",
                    )
                ],
            ]
        ),
    )


@bot.on_callback_query(CallbackButtonDataFilter("DELETE_CURRENT_LINE"))
async def deleteLineConfirm(_, query):
    sub_id = query.data.split("|")[1]
    delete_index = int(query.data.split("|")[2])
    message_id = await getLastMessageID(sub_id)
    await bot.edit_message_text(
        chat_id=query.from_user.id,
        message_id=message_id,
        text=f"<i>Deleting Line {delete_index} and re indexing...</i>\nPlease Wait",
    )
    await deleteSubtitleLine(delete_index, sub_id)
    await paginateLine(query)


async def deleteSubtitleLine(index_to_delete, sub_id):
    subtitles = await getSubtitleArray(sub_id)
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
    del srt_file[index_to_delete - 1]
    srt_file.clean_indexes()
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

    await UpdateSubtitleArray(sub_id, subtitle_data)
    return subtitle_data


@bot.on_callback_query(CallbackButtonDataFilter("CANCEL_DELETE_LINE"))
async def cancelDeleteLine(_, query):
    await paginateLine(query)
    return
