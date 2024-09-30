import pysrt
from datetime import datetime, timedelta
from subedit import bot
from subedit.helpers.Filters.custom_filters import CallbackButtonDataFilter
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from subedit.database.database import (
    getSubtitleArray,
    getLastMessageID,
    UpdateSubtitleArray, getLastIndexAndMessageIDCollabStatus, checkCollabMember, checkCollabMemberBlacklist,
)
from subedit.plugins.editor.line_pagination import paginateLine


@bot.on_callback_query(CallbackButtonDataFilter("ADD_NEW_LINE"))
async def addNewLine(_, query):
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
        text=f"This option can add a blank line with a duration of <i>2 seconds</i> after or before line number <i>{index}</i>.\n\nYou can edit the time code and text later.",
        message_id=message_id,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="⬆️ Insert Before",
                        callback_data=f"INSERT_NEW_LINE_BEFORE|{subtitle_id}|{index}",
                    ),
                    InlineKeyboardButton(
                        text="⬇️ Insert After",
                        callback_data=f"INSERT_NEW_LINE_AFTER|{subtitle_id}|{index}",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="❎ Cancel",
                        callback_data=f"CANCEL_ADD_LINE|{subtitle_id}|{index}",
                    )
                ],
            ]
        ),
    )


@bot.on_callback_query(CallbackButtonDataFilter("INSERT_NEW_LINE_AFTER"))
async def insertNewLineAfter(_, query):
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
    time_format = "%H:%M:%S,%f"
    start_timecode = str(srt_file[index - 1].end)
    # Parse the start time
    start = datetime.strptime(start_timecode, time_format)
    try:
        end_timecode = str(srt_file[index].start)
        # Parse the end time
        end = datetime.strptime(end_timecode, time_format)
    except Exception as e:
        end = start + timedelta(seconds=2)

    # Calculate the difference between the times
    difference = end - start

    # Check if the difference is more than 2 seconds
    if difference.total_seconds() > 2:
        # Create a new end time 2 seconds after the start time
        new_end = start + timedelta(seconds=2)

    else:
        new_end = end

    new_sub = pysrt.SubRipItem(
        index=len(srt_file) + 1,
        start=pysrt.SubRipTime(
            start.hour, start.minute, start.second, int(start.microsecond / 1000)
        ),
        end=pysrt.SubRipTime(
            new_end.hour,
            new_end.minute,
            new_end.second,
            int(new_end.microsecond / 1000),
        ),
        text="New Line",
    )
    srt_file.append(new_sub)
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


@bot.on_callback_query(CallbackButtonDataFilter("INSERT_NEW_LINE_BEFORE"))
async def insertNewLineBefore(_, query):
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
    time_format = "%H:%M:%S,%f"
    minimum_time = "00:00:00,000"
    minimum_time = datetime.strptime(minimum_time, time_format)
    end_timecode = str(srt_file[index - 1].start)
    # Parse the end time
    end = datetime.strptime(end_timecode, time_format)

    if index - 2 < 0:
        difference = end - minimum_time

        if difference.total_seconds() <= 2:
            new_start = minimum_time

        else:
            new_start = end - timedelta(seconds=2)

    else:
        start_timecode = str(srt_file[index - 2].end)
        # Parse the start time
        start = datetime.strptime(start_timecode, time_format)

        # Calculate the difference between the times
        difference = end - start

        # Check if the difference is more than 2 seconds
        if difference.total_seconds() > 2:
            # Create a new end time 2 seconds after the start time
            new_start = end - timedelta(seconds=2)

        else:
            new_start = start

    new_sub = pysrt.SubRipItem(
        index=len(srt_file) + 1,
        start=pysrt.SubRipTime(
            new_start.hour, new_start.minute, new_start.second, int(new_start.microsecond / 1000)
        ),
        end=pysrt.SubRipTime(
            end.hour,
            end.minute,
            end.second,
            int(end.microsecond / 1000),
        ),
        text="New Line",
    )
    srt_file.append(new_sub)
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


@bot.on_callback_query(CallbackButtonDataFilter("CANCEL_ADD_LINE"))
async def cancelAddLine(_, query):
    await paginateLine(query)
