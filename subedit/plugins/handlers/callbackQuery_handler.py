from subedit.helpers.Filters.custom_filters import (
    CallbackDataFilter,
    CallbackButtonDataFilter,
)
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from subedit.helpers.srt_parser import srtParser
from datetime import datetime, timezone
from subedit import bot
from subedit.plugins.handlers.message_handler import Editor
import os
import re
from subedit.logging import LOGGER


@bot.on_callback_query(CallbackDataFilter("START_NEW_BUTTON"))
async def callback_handler(client, query):
    print(query.data)
    new_session = await client.send_message(
        chat_id=query.from_user.id,
        text="Send the SRT file to start new editing session",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("❎ Cancel", callback_data="CANCEL_NEW_PROJECT")]]
        ),
    )
    try:
        response = await client.listen.Message(
            filters.document, filters.user(query.from_user.id), timeout=300
        )
    except TimeoutError:
        await client.send_message(
            chat_id=query.from_user.id,
            text="Timeout! Start new session again."
        )
    else:
        if response:
            await srtHandler(client, response)
            await new_session.delete()


@bot.on_callback_query(CallbackDataFilter("CANCEL_NEW_PROJECT"))
async def cancelProject(client, query):
    await client.listen.Cancel(filters.user(query.from_user.id))
    await Editor(query.from_user.id, query.message.id)


async def srtHandler(_, message):
    srt_file = message.document
    process_message = await message.reply(text="Processing...")
    download_dir = "downloads"
    os.makedirs(download_dir, exist_ok=True)
    file_path = await message.download(
        file_name=os.path.join(download_dir, srt_file.file_name)
    )
    print(file_path)
    sub_id = f"{message.from_user.id}{datetime.now(timezone.utc)}"
    sub_id = sub_id.replace(" ", "")
    sub_id = re.sub(r"\W+", "", sub_id)
    await process_message.edit_text(text=f"Processing {srt_file.file_name}")
    sub_parser = await srtParser(
        message.from_user.id, file_path, sub_id, srt_file.file_name
    )
    if sub_parser:
        await process_message.delete()
        os.remove(file_path)
        await bot.send_message(
            chat_id=message.from_user.id,
            text=f"Subtitle file <code>{srt_file.file_name}</code> has been processed successfully.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "🔭 Explore", switch_inline_query_current_chat=sub_id
                        ),
                        InlineKeyboardButton(
                            "📝 Edit", callback_data=f"EDIT_SUB|{sub_id}"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            "📦 Compile", callback_data=f"COMPILE_SUB|{sub_id}"
                        ),
                        InlineKeyboardButton(
                            "🗑️ Delete", callback_data=f"DELETE_SUB|{sub_id}"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            "♻️ Re-sync", callback_data=f"RESYNC_SUB|{sub_id}"
                        )
                    ]
                ]
            ),
        )
    else:
        await process_message.delete()
        os.remove(file_path)
        await bot.send_message(
            chat_id=message.from_user.id,
            text=f"Subtitles file <code>{srt_file.file_name}</code> could not be processed.\nTry again",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "📖 Start New", callback_data="START_NEW_BUTTON"
                        )
                    ]
                ]
            ),
        )


@bot.on_callback_query(CallbackButtonDataFilter("MAIN_MENU"))
async def editSub(_, query):
    sub_id = query.data.split("|")[1]
    await bot.send_message(
        chat_id=query.from_user.id,
        text="Select an option from below",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "🔭 Explore", switch_inline_query_current_chat=sub_id
                    ),
                    InlineKeyboardButton(
                        "📝 Edit", callback_data=f"EDIT_SUB|{sub_id}"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "📦 Compile", callback_data=f"COMPILE_SUB|{sub_id}"
                    ),
                    InlineKeyboardButton(
                        "🗑️ Delete", callback_data=f"DELETE_SUB|{sub_id}"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "♻️ Re-sync", callback_data=f"RESYNC_SUB|{sub_id}"
                    )
                ]
            ]
        ),
    )


@bot.on_callback_query(CallbackButtonDataFilter("START_EDIT_MENU"))
async def editSubMenu(_, query):
    await Editor(query.from_user.id, query.message.id)
