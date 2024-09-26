from subedit.helpers.Filters.custom_filters import (
    CallbackDataFilter,
    CallbackButtonDataFilter,
)
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from subedit.helpers.srt_parser import srtParser
from datetime import datetime, timezone
import time
from subedit import bot
from subedit.plugins.handlers.message_handler import Editor
import os
import re
import ffmpeg
from subedit.logging import LOGGER


@bot.on_callback_query(CallbackDataFilter("START_NEW_BUTTON"))
async def start_new_menu(client, query):
    await client.send_message(
        chat_id=query.from_user.id,
        text="Select an option from below",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🎞️ Extract from Video", callback_data="EXTRACT_FROM_VIDEO")],
             [InlineKeyboardButton("📜 Send SRT file", callback_data="SEND_SRT_FILE")],]
        )
    )


@bot.on_callback_query(CallbackDataFilter("SEND_SRT_FILE"))
async def callback_handler(client, query):
    print(query.data)
    new_session = await client.send_message(
        chat_id=query.from_user.id,
        text="Send the SRT file to start new editing session",
        reply_markup=InlineKeyboardMarkup(
            [
             [InlineKeyboardButton("❎ Cancel", callback_data="CANCEL_NEW_PROJECT")]
            ]
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


codecs = {
  "subrip": ".srt",
  "ass": ".ass",
  "mov_text": ".txt",
  "webvtt": ".vtt",
  "dvd_subtitle": ".sub",
  "pgs_subtitle": ".sup",
  "dvb_subtitle": ".sub",
  "mpl2": ".mpl",
  "microdvd": ".sub",
  "subviewer": ".sbv",
  "sami": ".smi",
  "realtext": ".rt",
  "stl": ".stl",
  "ttml": ".ttml",
  "vobsub": ".idx"
}


@bot.on_callback_query(CallbackDataFilter("EXTRACT_FROM_VIDEO"))
async def extract_from_video(client, query):
    msg = await client.send_message(
        chat_id=query.from_user.id,
        text="Forward or Send the video file to extract subtitles."
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
            await msg.delete()
            await client.listen.Cancel(filters.user(query.from_user.id))
            video_file = response.document
            process_message = await response.reply(text="Processing...")
            download_dir = "downloads"
            os.makedirs(download_dir, exist_ok=True)
            process_message = await process_message.edit_text(text="Downloading...")

            # Define the start time for tracking download speed
            start_time = time.time()

            file_path = await response.download(
                file_name=os.path.join(download_dir, video_file.file_name),
                progress=progress_bar,
                progress_args=(process_message, start_time)  # Pass the message and start time to the progress function
            )
            process_message = await process_message.edit_text(text="Extracting subtitles...")
            subtitle_tracks = get_subtitle_tracks(file_path)
            if not subtitle_tracks:
                await process_message.edit_text(text="No subtitle tracks found.")
                return
            file_name, extension = video_file.file_name.rsplit('.', 1)
            print(file_name)
            for track in subtitle_tracks:
                track_name = extract_subtitles(
                    file_path, track['index'], track['language'], track['codec'], file_name
                )
                await bot.send_document(
                    chat_id=query.from_user.id,
                    document=f"downloads/{track_name}",
                    caption=f"Compiled srt for {track_name}",
                )
                os.remove(f"downloads/{track_name}")
            os.remove(file_path)
            await process_message.delete()


async def progress_bar(current, total, process_message, start_time):
    elapsed_time = time.time() - start_time
    progress = f"{current * 100 / total:.1f}%"
    speed = current / elapsed_time if elapsed_time > 0 else 0
    speed_str = f"{speed / (1024 * 1024):.2f} MB/s"  # Speed in MB/s
    current_mb = current / (1024 * 1024)  # Convert bytes to MB
    total_mb = total / (1024 * 1024)  # Convert bytes to MB
    await process_message.edit_text(
        text=f"<i>Downloading... {progress}<i/> \n<b>File Size: {total_mb:.2f} MB \nDownloaded: {current_mb:.2f} MB ({speed_str})<b/>"
    )


def get_subtitle_tracks(input_file):
    # Probe the file to get the metadata (includes subtitle track details)
    probe = ffmpeg.probe(input_file)

    subtitle_tracks = []

    # Loop through streams to find subtitle tracks
    for stream in probe['streams']:
        if stream['codec_type'] == 'subtitle':
            track_info = {
                'index': stream['index'],  # Track index
                'codec': stream.get('codec_name', 'unknown'),  # Codec type (e.g., 'srt', 'ass')
                'language': stream['tags'].get('title', 'unknown'),  # Language if available
                'language_code': stream['tags'].get('language', 'unknown')  # Language if available
            }
            subtitle_tracks.append(track_info)

    return subtitle_tracks


def extract_subtitles(input_file, track_index, language, codec, file_name):
    # Ensure the codec exists in the dictionary
    if codec not in codecs:
        raise ValueError(f"Unknown codec '{codec}'. Cannot determine file extension.")

    # Create a suitable output filename based on track details
    output_file = f'{file_name}.{language}{codecs[codec]}'

    # Ensure "downloads" directory exists
    output_directory = "downloads"
    os.makedirs(output_directory, exist_ok=True)

    # Set the full output path
    output_file_path = os.path.join(output_directory, output_file)

    # Extract the subtitle track
    try:
        (
            ffmpeg
            .input(input_file)
            .output(output_file_path, map=f'0:{track_index}', y=None)  # Using the track index to map the right subtitle
            .run()
        )
        print(f"Extracted subtitles for track {track_index} (language: {language}) to {output_file}")
    except ffmpeg.Error as e:
        print(f"An error occurred: {e.stderr.decode('utf-8')}")

    return output_file