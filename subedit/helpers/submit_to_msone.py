import base64
import json
import re
import requests
from subedit.config import MAIL_API

from subedit.database.database import getLastIndexAndMessageIDCollabStatus, getCollabAdmin, getSubtitleDocument
from subedit.helpers.Filters.custom_filters import (
    CallbackButtonDataFilter,
)
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from subedit import bot
from subedit.plugins.editor.compile_subtitle import compileEditedSRT, compileOriginalSRT
import os
from asyncio import CancelledError, create_task, TimeoutError

subtitle_data = {}


@bot.on_callback_query(CallbackButtonDataFilter("SUBMIT_TO_MSONE"))
async def submitToSMSone(client, query):
    subtitle_id = query.data.split("|")[1]
    user_id = query.from_user.id
    try:
        await client.listen.Cancel(filters.user(user_id))
    except:
        pass
    index, msg_id, collab_status = await getLastIndexAndMessageIDCollabStatus(subtitle_id)
    if collab_status:
        if await getCollabAdmin(subtitle_id) != user_id:
            await query.answer("⛔️️ You are not authorized to submit this subtitle.", show_alert=True)
            return

    await bot.edit_message_text(message_id=query.message.id,
                          chat_id=user_id,
                          text='Please select and option from below.\nIf you are new to MSone, click on the "👦🏻 Fresher" button to submit your first 50 lines to <b>MSone</b>.\nFor others, click on the "👨🏻 Existing Translators" button to submit your subtitles to MSone.',
                          reply_markup=InlineKeyboardMarkup(
                              [
                                  [InlineKeyboardButton("👦🏻 Fresher",
                                                        callback_data=f"SUBMIT_TO_MSONE_FRESHER|{subtitle_id}")],
                                  [InlineKeyboardButton("👨🏻 Existing Translators",
                                                        callback_data=f"SUBMIT_TO_MSONE_EXISTING|{subtitle_id}")],
                                  [InlineKeyboardButton("❎ Cancel",
                                                        callback_data=f"MAIN_MENU|{subtitle_id}")]
                          ]
                          )
                          )



@bot.on_callback_query(CallbackButtonDataFilter("SUBMIT_TO_MSONE_FRESHER"))
async def submitToSMSoneFresher(_, query):
    subtitle_id = query.data.split("|")[1]
    user_id = query.from_user.id
    index, msg_id, collab_status = await getLastIndexAndMessageIDCollabStatus(subtitle_id)
    if collab_status:
        if await getCollabAdmin(subtitle_id) != user_id:
            await query.answer("⛔️️ You are not authorized to submit this subtitle.", show_alert=True)
            return

    await query.message.edit_text(text="By clicking continue, you agree to the following terms and conditions:\n\n"
                                       "● You agree to submit the first 50 lines of the subtitle to MSone for verification.\n"
                                       "● You agree to not use this platform for any illegal or malicious purposes.\n"
                                       "● You agree to share your name and email address with MSone for verification purposes.",
                                       reply_markup=InlineKeyboardMarkup([
                                           [InlineKeyboardButton("⏩ Continue", callback_data=f"SUBMIT_FRESHER_SUBMIT|{subtitle_id}")],
                                           [InlineKeyboardButton("❎ Cancel", callback_data=f"SUBMIT_TO_MSONE|{subtitle_id}")],
                                       ]
                                  )
                                  )


@bot.on_callback_query(CallbackButtonDataFilter("SUBMIT_TO_MSONE_EXISTING"))
async def submitToSMSoneExisting(_, query):
    subtitle_id = query.data.split("|")[1]
    user_id = query.from_user.id
    index, msg_id, collab_status = await getLastIndexAndMessageIDCollabStatus(subtitle_id)
    if collab_status:
        if await getCollabAdmin(subtitle_id) != user_id:
            await query.answer("⛔️️ You are not authorized to submit this subtitle.", show_alert=True)
            return

    await query.message.edit_text(text="By clicking continue, you agree to the following terms and conditions:\n\n"
                                       "● You agree to submit the subtitle to MSone for verification.\n"
                                       "● You agree to not use this platform for any illegal or malicious purposes.\n"
                                       "● You agree to share your name and email address with MSone for verification purposes.",
                                       reply_markup=InlineKeyboardMarkup([
                                           [InlineKeyboardButton("⏩ Continue", callback_data=f"SUBMIT_EXISTING_SUBMIT|{subtitle_id}")],
                                           [InlineKeyboardButton("❎ Cancel", callback_data=f"SUBMIT_TO_MSONE|{subtitle_id}")],
                                       ]
                                  )
                                  )


@bot.on_callback_query(CallbackButtonDataFilter("SUBMIT_FRESHER_SUBMIT"))
async def submitToMSoneFresherSubmit(client, query):
    await submitToMSoneForm(client, query, "SBMTTOMSONEFRSHRSBMTCNFRM")


@bot.on_callback_query(CallbackButtonDataFilter("SUBMIT_EXISTING_SUBMIT"))
async def submitToMSoneExistingSubmit(client, query):
    await submitToMSoneForm(client, query, "SBMTTOMSONEXSTGSBMTCNFRM")


form_state = {}


async def submitToMSoneForm(client, query, submit_button_data):
    subtitle_id = query.data.split("|")[1]
    user_id = query.from_user.id
    # Reset user data for new form submission
    subtitle_data.pop(user_id, None)

    try:
        # Ask for the movie title (Non-empty validation)
        title = await ask_for_input(
            client, user_id,
            query_message="സിനിമയുടെ പേര്:",
            cancel_callback_data="CANCEL_SUBMIT_TO_MSONE",
            subtitle_id=subtitle_id,
            validation_fn=validate_non_empty,
            error_message="❌ ദയവായി സിനിമയുടെ പേര് നൽകുക."
        )
        if title is None:  # Check if user cancelled
            return

        # Ask for the release year with validation
        year = await ask_for_input(
            client, user_id,
            query_message="സിനിമ റിലീസായ വര്‍ഷം:",
            cancel_callback_data="CANCEL_SUBMIT_TO_MSONE",
            subtitle_id=subtitle_id,
            validation_fn=validate_year,
            error_message="❌ ദയവായി 4 അക്കമുള്ള ശരിയായ ഒരു വർഷം നൽകുക."
        )
        if year is None:  # Check if user cancelled
            return

        # Ask for the translator's name (Non-empty validation)
        translator_name = await ask_for_input(
            client, user_id,
            query_message="പരിഭാഷകന്‍റെ പേര് മലയാളത്തില്‍:",
            cancel_callback_data="CANCEL_SUBMIT_TO_MSONE",
            subtitle_id=subtitle_id,
            validation_fn=validate_non_empty,
            error_message="❌ ദയവായി പരിഭാഷകന്‍റെ പേരു നൽകുക."
        )
        if translator_name is None:  # Check if user cancelled
            return

        # Ask for the email with validation
        email = await ask_for_input(
            client, user_id,
            query_message="ഇ-മെയില്‍:",
            cancel_callback_data="CANCEL_SUBMIT_TO_MSONE",
            subtitle_id=subtitle_id,
            validation_fn=validate_email,
            error_message="❌ ദയവായി ശരിയായ ഒരു ഇമെയിൽ വിലാസം നൽകുക."
        )
        if email is None:  # Check if user cancelled
            return

        # Ask for the contact ID (Non-empty validation)
        contact_id = await ask_for_input(
            client, user_id,
            query_message="FB/Insta/Telegram ID:",
            cancel_callback_data="CANCEL_SUBMIT_TO_MSONE",
            subtitle_id=subtitle_id,
            validation_fn=validate_non_empty,
            error_message="❌ ദയവായി നിങ്ങളെ ബന്ധപ്പെടാനുള്ള ഒരു ഐഡി‍ നല്‍കുക."
        )
        if contact_id is None:  # Check if user cancelled
            return

        # Ask for the file link with URL validation
        file_link = await ask_for_input(
            client, user_id,
            query_message="സിങ്കാകുന്ന സിനിമാ ഫയലിന്‍റെ ടോറന്‍റ് ഇന്‍ഫോ / ടെലിഗ്രാം ലിങ്ക്:",
            cancel_callback_data="CANCEL_SUBMIT_TO_MSONE",
            subtitle_id=subtitle_id,
            validation_fn=validate_link,
            error_message="❌ ദയവായി ശരിയായ ലിങ്ക് നൽകുക."
        )
        if file_link is None:  # Check if user cancelled
            return

        # Ask for the IMDB link with URL validation
        imdb_link = await ask_for_input(
            client, user_id,
            query_message="സിനിമയുടെ IMDB ലിങ്ക്:",
            cancel_callback_data="CANCEL_SUBMIT_TO_MSONE",
            subtitle_id=subtitle_id,
            validation_fn=validate_link,
            error_message="❌ ദയവായി ശരിയായ ലിങ്ക് നൽകുക."
        )
        if imdb_link is None:  # Check if user cancelled
            return

        # Ask for the synopsis with Non-empty validation
        synopsis = await ask_for_input(
            client, user_id,
            query_message="സിനിമയുടെ സിനോപ്സിസ് മലയാളത്തില്‍:",
            cancel_callback_data="CANCEL_SUBMIT_TO_MSONE",
            subtitle_id=subtitle_id,
            validation_fn=validate_non_empty,
            error_message="❌ ദയവായി ഒരു സിനോപ്സിസ് നല്‍കുക."
        )
        if synopsis is None:  # Check if user cancelled
            return

        # Store the collected data
        subtitle_data[user_id] = {
            "title": title,
            "year": year,
            "translator_name": translator_name,
            "email": email,
            "contact_id": contact_id,
            "file_link": file_link,
            "imdb_link": imdb_link,
            "synopsis": synopsis
        }

        # Send confirmation message with the collected data
        await bot.send_message(
            chat_id=user_id,
            text=f"നിങ്ങള്‍ നല്‍കിയ വിവരങ്ങള്‍ ശരിയാണോയെന്ന് ഉറപ്പുവരുത്തുക:\n\n"
                 f"**സിനിമയുടെ പേര്: {title}\n\n**"
                 f"**റിലീസായ വര്‍ഷം: {year}\n\n**"
                 f"**പരിഭാഷകന്‍റെ പേര്: {translator_name}\n\n**"
                 f"**ഇ-മെയില്‍: {email}\n\n**"
                 f"**ബന്ധപ്പെടാനുള്ള ഐഡി: {contact_id}\n\n**"
                 f"**സിനിമയുടെ ലിങ്ക്: {file_link}\n\n**"
                f"**IMDB ലിങ്ക്: {imdb_link}\n\n**"
                f"**സിനോപ്സിസ്: {synopsis}**",

            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📤 Submit", callback_data=f"{submit_button_data}|{subtitle_id}")],
                [InlineKeyboardButton("❎ Cancel", callback_data=f"SUBMIT_TO_MSONE|{subtitle_id}")],
            ])
        )
    except (CancelledError, Exception) as e:
        # Handle form cancellation and clean up
        await bot.send_message(
            chat_id=user_id,
            text="❌ Form submission has been canceled.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📤 Submit to MSone",
                                      callback_data=f"SUBMIT_TO_MSONE|{subtitle_id}")],
            ])
        )

# Dictionary to track active input tasks
active_tasks = {}


# Helper function to ask for user input with validation
async def ask_for_input(client, user_id, query_message, subtitle_id, cancel_callback_data, validation_fn=None,
                        error_message=None):
    # Create a task for listening to user input
    task = create_task(
        _listen_for_input(client, user_id, query_message, subtitle_id, cancel_callback_data, validation_fn,
                          error_message))
    active_tasks[user_id] = task

    try:
        # Await the task and get the input
        result = await task
        return result
    except CancelledError:
        raise Exception("Input process was cancelled.")


async def _listen_for_input(client, user_id, query_message, subtitle_id, cancel_callback_data, validation_fn,
                            error_message):
    prompt_message = await bot.send_message(chat_id=user_id, text=query_message,
                                            reply_markup=InlineKeyboardMarkup([
                                                [InlineKeyboardButton("❎ Cancel",
                                                                      callback_data=f"{cancel_callback_data}|{subtitle_id}")],
                                            ]))

    try:
        form_message = await client.listen.Message(id=filters.user(user_id), timeout=300)
        user_input = form_message.text

        # Perform validation
        if validation_fn and not validation_fn(user_input):
            await bot.send_message(chat_id=user_id, text=error_message)
            return await _listen_for_input(client, user_id, query_message, subtitle_id, cancel_callback_data,
                                           validation_fn, error_message)

        return user_input

    except TimeoutError:
        await bot.send_message(chat_id=user_id, text="❌ Timeout. Please start the process again.",
                               reply_markup=InlineKeyboardMarkup([
                                      [InlineKeyboardButton("📤 Submit to MSone",
                                                            callback_data=f"SUBMIT_TO_MSONE|{subtitle_id}")],
                                  ]))
        return None


@bot.on_callback_query(CallbackButtonDataFilter("CANCEL_SUBMIT_TO_MSONE"))
async def cancel_submission(client, query):
    user_id = query.from_user.id
    await client.listen.Cancel(filters.user(user_id))

    # Cancel the active task for this user if exists
    task = active_tasks.get(user_id)
    if task:
        task.cancel()

    subtitle_data.pop(user_id, None)  # Clear user data if they cancel


# Define validation functions
def validate_year(year):
    return year.isdigit() and len(year) == 4  # Example: Year should be 4 digits

def validate_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)  # Simple email validation

def validate_non_empty(input_text):
    return bool(input_text.strip())  # Ensures the input is not just empty or spaces

def validate_link(link):
    return re.match(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", link)  # Basic URL validation


@bot.on_callback_query(CallbackButtonDataFilter("SBMTTOMSONEFRSHRSBMTCNFRM"))
async def submitToMSoneFresherSubmitConfirm(client, query):
    await submitToMSoneConfirm(client, query, "fresher")


@bot.on_callback_query(CallbackButtonDataFilter("SBMTTOMSONEXSTGSBMTCNFRM"))
async def submitToMSoneExistingSubmitConfirm(client, query):
    await submitToMSoneConfirm(client, query, "main")


async def submitToMSoneConfirm(client, query, mail_type):
    subtitle_id = query.data.split("|")[1]
    user_id = query.from_user.id
    await query.message.edit_text("Compiling your subtitles, please wait...")
    subtitle_document = await getSubtitleDocument(subtitle_id)
    file_name = subtitle_document["file_name"]
    file_name_root, file_extension = os.path.splitext(file_name)
    file_name_new = f"{file_name_root}.MSONE{file_extension}"
    # print(file_name)
    subtitles = subtitle_document["subtitles"]
    await compileEditedSRT(subtitles, file_name_new)
    await compileOriginalSRT(subtitles, file_name)
    await query.message.edit_text("Submitting...")
    response = await submitToMSoneAPI(file_name, file_name_new, mail_type, subtitle_data[user_id])
    if response:
        await query.message.edit_text(text="🥳 Your subtitles have been submitted successfully!",
                                      reply_markup=InlineKeyboardMarkup([
                                          [InlineKeyboardButton("💠 Main Menu",
                                                            callback_data=f"MAIN_MENU|{subtitle_id}")],
                                      ])
                                      )

    else:
        await query.message.edit_text(text="⚠️ Failed to submit your subtitles. Please try again.",
                                      reply_markup=InlineKeyboardMarkup([
                                          [InlineKeyboardButton("📤 Submit to MSone",
                                                            callback_data=f"SUBMIT_TO_MSONE|{subtitle_id}")],
                                      ])
                                      )


async def submitToMSoneAPI(original_subtitle, edited_subtitle, mail_type, translator_data_dict):

    headers = {
        'Content-Type': 'application/json',
    }


    with open(f"downloads/{original_subtitle}", "rb") as file:
        file_content = file.read()
        file_data_encoded_original = base64.b64encode(file_content).decode("utf-8")

    with open(f"downloads/{edited_subtitle}", "rb") as file:
        file_content = file.read()
        file_data_encoded_edited = base64.b64encode(file_content).decode("utf-8")


    attachments = [
        {
            'name': original_subtitle,
            'data': file_data_encoded_original
        },
        {
            'name' : edited_subtitle,
            'data' : file_data_encoded_edited
        }
    ]

    payload = {
        'to': mail_type,
        'subject': f'{translator_data_dict["title"]} ({translator_data_dict["year"]})',
        'message': f'<b>Movie Name:</b> {translator_data_dict["title"]} {translator_data_dict["year"]}<br>'
                   f'<b>Translator Name:</b> {translator_data_dict["translator_name"]}<br>'
                   f'<b>Email:</b> {translator_data_dict["email"]}<br>'
                   f'<b>Telegram ID:</b> {translator_data_dict["contact_id"]}<br>'
                   f'<b>Torrent Info:</b> {translator_data_dict["file_link"]}<br>'
                   f'<b>IMDB Link:</b> {translator_data_dict["imdb_link"]}<br>'
                   f'<b>Synopsis:</b>  <p>{translator_data_dict["synopsis"]}</p><br><br>'
                   f'Submitted from <i><b>MSone SubEditor Bot</b></i>',
        'headers': ['Content-Type: text/html; charset=UTF-8'],
        'attachments': attachments
    }
    # print(payload)
    response = requests.post(MAIL_API, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        print('Email sent successfully')
        return True
    else:
        print(f'Error: {response.status_code}, {response.content}')
        return False
