import pysrt
from subedit import bot
from subedit.helpers.Filters.custom_filters import CallbackButtonDataFilter
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from subedit.database.database import (
    getSubtitleArray,
    getLastMessageID,
    UpdateSubtitleArray,
)
from subedit.plugins.editor.line_pagination import paginateLine


@bot.on_callback_query(CallbackButtonDataFilter("MERGE_LINE"))
async def mergeLine(_, query):
    subtitle_id = query.data.split("|")[1]
    index = int(query.data.split("|")[2])
    message_id = await getLastMessageID(subtitle_id)
    await bot.edit_message_text(
        chat_id=query.from_user.id,
        text=f"This will merge the current line with the option you give",
        message_id=message_id,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="🔗 Merge with previous",
                        callback_data=f"MERGE_PREV_LINE|{subtitle_id}|{index}",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🔗 Merge with next",
                        callback_data=f"MERGE_NEXT_LINE|{subtitle_id}|{index}",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="❎ Cancel",
                        callback_data=f"CANCEL_MERGE_LINE|{subtitle_id}|{index}",
                    )
                ],
            ]
        ),
    )


@bot.on_callback_query(CallbackButtonDataFilter("MERGE_PREV_LINE"))
async def mergePrevLine(_, query):
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
    # Merge two subtitle items
    srt_file[index - 2].text += "\n" + srt_file[index - 1].text
    srt_file[index - 2].end = srt_file[index - 1].end

    # Remove the second item using list operations
    del srt_file[index - 1]

    # Clean up the indexes
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


@bot.on_callback_query(CallbackButtonDataFilter("MERGE_NEXT_LINE"))
async def mergeNextLine(_, query):
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
    # Merge two subtitle items
    srt_file[index - 1].text += "\n" + srt_file[index].text
    srt_file[index - 1].end = srt_file[index].end

    # Remove the second item using list operations
    del srt_file[index]

    # Clean up the indexes
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


@bot.on_callback_query(CallbackButtonDataFilter("CANCEL_MERGE_LINE"))
async def cancelMergeLine(_, query):
    await paginateLine(query)
