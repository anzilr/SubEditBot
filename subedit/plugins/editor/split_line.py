import pysrt
from subedit import bot
from subedit.helpers.Filters.custom_filters import CallbackButtonDataFilter
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from subedit.database.database import (
    getSubtitleArray,
    getLastMessageID,
    UpdateSubtitleArray, getLastIndexAndMessageIDCollabStatus, checkCollabMember, checkCollabMemberBlacklist,
)
from subedit.plugins.editor.line_pagination import paginateLine


@bot.on_callback_query(CallbackButtonDataFilter("SPLIT_LINE"))
async def splitLine(_, query):
    subtitle_id = query.data.split("|")[1]
    index = int(query.data.split("|")[2])
    # message_id = await getLastMessageID(subtitle_id)
    indexx, message_id, collab_status = await getLastIndexAndMessageIDCollabStatus(subtitle_id)
    if collab_status:
        if not await checkCollabMember(subtitle_id, query.from_user.id):
            await query.answer("⛔️️ You are not authorized to edit this subtitle.", show_alert=True)
            return
        if await checkCollabMemberBlacklist(subtitle_id, query.from_user.id):
            await query.answer("⛔️️️ You are on the blacklist for this subtitle.", show_alert=True)
            return
    await bot.edit_message_text(
        chat_id=query.from_user.id,
        text=f"This will split the current line at the middle of the time.\nYou can edit the time and text later.\n\n(More line split features coming soon)",
        message_id=message_id,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="✂️ Split the line",
                        callback_data=f"SPLIT_THE_LINE|{subtitle_id}|{index}",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="❎ Cancel",
                        callback_data=f"CANCEL_SPLIT_LINE|{subtitle_id}|{index}",
                    )
                ],
            ]
        ),
    )


@bot.on_callback_query(CallbackButtonDataFilter("SPLIT_THE_LINE"))
async def splitTheLine(_, query):
    subtitle_id = query.data.split("|")[1]
    index = int(query.data.split("|")[2])
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
    # Calculate the midpoint of the subtitle duration
    start = srt_file[index - 1].start.ordinal
    end = srt_file[index - 1].end.ordinal
    mid_time = start + (end - start) // 2

    # Convert mid_time back to SubRipTime
    mid_time = pysrt.SubRipTime(milliseconds=mid_time)

    # Create a new subtitle item starting from the midpoint to the end time
    new_sub = pysrt.SubRipItem(
        index=len(srt_file) + 1,  # Set the new subtitle's index
        start=mid_time,
        end=srt_file[index - 1].end,
        text=srt_file[index - 1].text,
    )

    # Adjust the end time of the original subtitle to the midpoint
    srt_file[index - 1].end = mid_time

    # Append the new subtitle to the end of the file
    srt_file.append(new_sub)
    # Clean the indexes of the file to avoid duplicate indexes
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

    await UpdateSubtitleArray(subtitle_id, subtitle_data)
    await paginateLine(query)


@bot.on_callback_query(CallbackButtonDataFilter("CANCEL_SPLIT_LINE"))
async def cancelSplitLine(_, query):
    await paginateLine(query)
