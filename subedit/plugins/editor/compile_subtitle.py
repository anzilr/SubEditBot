from subedit import bot
import pysrt
import os
from typing import List, Dict, Any
from subedit.helpers.Filters.custom_filters import CallbackButtonDataFilter
from subedit.database.database import getSubtitleDocument


@bot.on_callback_query(CallbackButtonDataFilter("COMPILE_SUB"))
async def compileSubtitle(_, query):
    subtitle_id = query.data.split("|")[1]
    msg = await bot.send_message(
        chat_id=query.from_user.id, text="Compiling the srt, please wait..."
    )
    subtitle_document = await getSubtitleDocument(subtitle_id)
    file_name = subtitle_document["file_name"]
    print(file_name)
    subtitles = subtitle_document["subtitles"]
    await compileSRT(subtitles, file_name)
    await bot.send_document(
        chat_id=query.from_user.id,
        document=f"downloads/{file_name}",
        caption=f"Compiled srt for {file_name}",
    )
    await msg.delete()
    os.remove(f"downloads/{file_name}")


async def compileSRT(subtitles: List[Dict[str, Any]], output_file: str):
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
            text=original_text if edited_text is None else edited_text,
        )
        srt_items.append(srt_item)
    # Create SubRipFile with all items at once
    srt_file = pysrt.SubRipFile(items=srt_items)
    # Save SubRipFile to SRT file
    output_file_path = os.path.join("downloads", output_file)
    srt_file.save(output_file_path, encoding="utf-8")
