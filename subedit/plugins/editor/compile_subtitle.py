from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from subedit import bot
import pysrt
import os
from typing import List, Dict, Any
from subedit.helpers.Filters.custom_filters import CallbackButtonDataFilter
from subedit.database.database import getSubtitleDocument, getLastIndexAndMessageIDCollabStatus, checkCollabMember, \
    checkCollabMemberBlacklist


@bot.on_callback_query(CallbackButtonDataFilter("COMPILE_SUB"))
async def compileSubtitleFile(_, query):
    subtitle_id = query.data.split("|")[1]
    await query.message.edit_text("Select an option",
                                  reply_markup=InlineKeyboardMarkup(
                                      [
                                          [
                                              InlineKeyboardButton(
                                                  text="📦 Compile Original",
                                                  callback_data=f"COMPILE_ORIGINAL|{subtitle_id}"
                                              ),
                                              InlineKeyboardButton(
                                                  text="📦 Compile Edited",
                                                  callback_data=f"COMPILE_EDITED|{subtitle_id}"
                                              )
                                          ],
                                          [
                                              InlineKeyboardButton(
                                                  text="🔙",
                                                  callback_data=f"MAIN_MENU|{subtitle_id}"
                                              )
                                          ],
                                      ]
                                  )
                                  )


@bot.on_callback_query(CallbackButtonDataFilter("COMPILE_ORIGINAL"))
async def compileOriginal(client, query):
    await compileSubtitle(query, "ORIGINAL")


@bot.on_callback_query(CallbackButtonDataFilter("COMPILE_EDITED"))
async def compileEdited(client, query):
    await compileSubtitle(query, "EDITED")


async def compileSubtitle(query, sub_type):
    subtitle_id = query.data.split("|")[1]
    indexx, message_id, collab_status = await getLastIndexAndMessageIDCollabStatus(subtitle_id)
    if collab_status:
        if not await checkCollabMember(subtitle_id, query.from_user.id):
            await query.answer("⛔️️ You are not authorized to edit this subtitle.", show_alert=True)
            return
        if await checkCollabMemberBlacklist(subtitle_id, query.from_user.id):
            await query.answer("⛔️️️ You are on the blacklist for this subtitle.", show_alert=True)
            return
    msg = await bot.send_message(
        chat_id=query.from_user.id, text="Compiling the srt, please wait..."
    )
    subtitle_document = await getSubtitleDocument(subtitle_id)
    file_name = subtitle_document["file_name"]
    print(file_name)
    subtitles = subtitle_document["subtitles"]
    if sub_type == "EDITED":
        file_name_root, file_extension = os.path.splitext(file_name)
        file_name = f"{file_name_root}.MSONE{file_extension}"
        await compileEditedSRT(subtitles, file_name)
    elif sub_type == "ORIGINAL":
        await compileOriginalSRT(subtitles, file_name)
    await bot.send_document(
        chat_id=query.from_user.id,
        document=f"downloads/{file_name}",
        caption=f"Compiled srt for {file_name}",
    )
    await msg.delete()
    os.remove(f"downloads/{file_name}")


async def compileEditedSRT(subtitles: List[Dict[str, Any]], output_file: str):
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


async def compileOriginalSRT(subtitles: List[Dict[str, Any]], output_file: str):
    srt_items = []
    for subtitle in subtitles:
        start_time = pysrt.SubRipTime.from_string(subtitle["start_time"])
        end_time = pysrt.SubRipTime.from_string(subtitle["end_time"])
        original_text = subtitle["original"]

        # Create SubRipItem but delay appending to list
        srt_item = pysrt.SubRipItem(
            index=subtitle["index"],
            start=start_time,
            end=end_time,
            text=original_text,
        )
        srt_items.append(srt_item)
    # Create SubRipFile with all items at once
    srt_file = pysrt.SubRipFile(items=srt_items)
    # Save SubRipFile to SRT file
    output_file_path = os.path.join("downloads", output_file)
    srt_file.save(output_file_path, encoding="utf-8")
