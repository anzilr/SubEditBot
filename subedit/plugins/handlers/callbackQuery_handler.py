import asyncio

from subedit.database.database import getLastIndexAndMessageIDCollabStatus, checkCollabMember, \
    checkCollabMemberBlacklist
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
import math


@bot.on_callback_query(CallbackDataFilter("START_NEW_BUTTON"))
async def start_new_menu(client, query):
    await client.send_message(
        chat_id=query.from_user.id,
        text="Select an option from below",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🎞️ Extract from Video", callback_data="EXTRACT_FROM_VIDEO")],
             [InlineKeyboardButton("📜 Send SRT file", callback_data="SEND_SRT_FILE")],
             [InlineKeyboardButton("🔙", callback_data="START_EDIT_MENU")]]
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
                        ),
                        InlineKeyboardButton(
                            "👫 Collaborate", callback_data=f"COLLAB_MENU|{sub_id}"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "📤 Submit to MSone", callback_data=f"SUBMIT_TO_MSONE|{sub_id}"
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
                            "🔙", callback_data="START_EDIT_MENU"
                        )
                    ]
                ]
            ),
        )


@bot.on_callback_query(CallbackButtonDataFilter("MAIN_MENU"))
async def editSub(client, query):
    sub_id = query.data.split("|")[1]
    user_id = query.from_user.id
    try:
        await client.listen.Cancel(filters.user(user_id))
    except:
        pass
    index, msg_id, collab_status = await getLastIndexAndMessageIDCollabStatus(sub_id)
    if collab_status:
        if not await checkCollabMember(sub_id, user_id):
            await query.answer("⛔️️ You are not authorized to edit this subtitle.", show_alert=True)
            return

        elif await checkCollabMemberBlacklist(sub_id, user_id):
            await query.answer("⛔️️️ You are on the blacklist for this subtitle.", show_alert=True)
            return
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
                    ),
                    InlineKeyboardButton(
                        "👫 Collaborate", callback_data=f"COLLAB_MENU|{sub_id}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "📤 Submit to MSone", callback_data=f"SUBMIT_TO_MSONE|{sub_id}"
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

# Dictionary to track cancel events
cancel_events = {}
download_tasks = {}



@bot.on_callback_query(CallbackButtonDataFilter("CANCEL_DOWNLOAD"))
async def handle_callback(client, query):
    if query.data.startswith("CANCEL_DOWNLOAD|"):
        user_id = int(query.data.split("|")[1])
        if query.from_user.id == user_id:
            # Set the cancel event for this user
            if user_id in cancel_events:
                cancel_events[user_id].set()

                # Cancel the download task if it's still running
                if user_id in download_tasks:
                    download_task = download_tasks[user_id]
                    if not download_task.done():
                        download_task.cancel()

                await query.message.edit_text("Download canceled.")
                await query.answer("Download canceled!")

                # Remove the cancel event and task from the dictionaries
                cancel_events.pop(user_id, None)
                download_tasks.pop(user_id, None)

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

            # Create a cancel event and store it in the dictionary
            cancel_event = asyncio.Event()
            cancel_events[query.from_user.id] = cancel_event

            # Add a cancel button
            cancel_button = InlineKeyboardMarkup(
                [[InlineKeyboardButton("Cancel", callback_data=f"CANCEL_DOWNLOAD|{query.from_user.id}")]]
            )
            process_message = await response.reply(
                text="Processing...",
                reply_markup=cancel_button
            )

            download_dir = "downloads"
            os.makedirs(download_dir, exist_ok=True)
            process_message = await process_message.edit_text(text="Downloading...", reply_markup=cancel_button)

            # Define the start time for tracking download speed
            start_time = time.time()

            # Track the download task
            download_task = None

            try:
                # Start file download with progress tracking
                download_task = asyncio.create_task(response.download(
                    file_name=os.path.join(download_dir, video_file.file_name),
                    progress=progress_bar,
                    progress_args=(process_message, start_time, cancel_button, 5, query.from_user.id)  # Pass user ID to progress
                ))

                # Store the task reference
                download_tasks[query.from_user.id] = download_task

                file_path = await download_task

            except asyncio.CancelledError:
                await process_message.edit_text(text="Download canceled.",
                                                reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙", callback_data=f"START_NEW_BUTTON")]]
            ))
                return  # Stop further processing

            # Proceed with subtitle extraction if download wasn't canceled
            if not cancel_event.is_set():
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

            # Cleanup the cancel event after processing completes
            cancel_events.pop(query.from_user.id, None)
            download_tasks.pop(query.from_user.id, None)



# Helper function to convert bytes to a human-readable format
def humanbytes(size):
    # Convert bytes to the most suitable unit (KB, MB, GB, etc.)
    power = 2**10
    n = 0
    power_labels = {0: '', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
    while size > power:
        size /= power
        n += 1
    return f"{round(size, 2)} {power_labels[n]}"

# Helper function to format time into a human-readable string
def TimeFormatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(milliseconds, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = (
        (f"{days}d " if days else "") +
        (f"{hours}h " if hours else "") +
        (f"{minutes}m " if minutes else "") +
        (f"{seconds}s " if seconds else "")
    )
    return tmp or "0s"

async def progress_bar(current, total, process_message, start_time, cancel_button, delay=5, user_id=None):
    now = time.time()
    elapsed_time = now - start_time

    # Track the time of the last message update
    if not hasattr(progress_bar, "last_update"):
        progress_bar.last_update = 0

    # Calculate download progress percentage
    percentage = current * 100 / total

    # Calculate download speed (bytes per second)
    speed = current / elapsed_time if elapsed_time > 0 else 0

    # Convert elapsed time and calculate estimated time to completion
    elapsed_time_ms = round(elapsed_time) * 1000
    time_to_completion = round((total - current) / speed) * 1000 if speed > 0 else 0
    estimated_total_time = elapsed_time_ms + time_to_completion

    # Format elapsed time and ETA
    elapsed_time_str = TimeFormatter(milliseconds=elapsed_time_ms)
    estimated_total_time_str = TimeFormatter(milliseconds=estimated_total_time)

    # Create a visual progress bar
    progress = "🔰 [{0}{1}] \n\n🧮 P: {2}%\n\n".format(
        ''.join(["█" for _ in range(math.floor(percentage / 5))]),
        ''.join(["░" for _ in range(20 - math.floor(percentage / 5))]),
        round(percentage, 2)
    )

    # Prepare the progress message
    tmp = progress + "🗂 {0} of {1}\n\n🚀 Speed: {2}/s\n\n⏰ ETA: {3}\n\n".format(
        humanbytes(current),
        humanbytes(total),
        humanbytes(speed),
        estimated_total_time_str if estimated_total_time_str != '' else "0 s"
    )

    # Check if the cancel event has been set for this user
    if user_id in cancel_events and cancel_events[user_id].is_set():
        return  # Stop the progress tracking

    # Update the progress message only if the specified delay has passed
    if (now - progress_bar.last_update) >= delay or current == total:
        try:
            await process_message.edit_text(
                text=f"<i>📥 Downloading...</i>\n\n{tmp}",
                reply_markup=cancel_button
            )
            # Record the last update time
            progress_bar.last_update = now
        except Exception as e:
            print(f"Failed to update progress: {e}")

    # Return the updated start time for the next check
    return start_time



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
    # if codec not in codecs:

        # raise ValueError(f"Unknown codec '{codec}'. Cannot determine file extension.")

    # Create a suitable output filename based on track details
    output_file = f'{file_name}.{language}{codecs[codec] if codec in codecs else ".srt"}'

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