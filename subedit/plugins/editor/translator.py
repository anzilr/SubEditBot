import asyncio
from subedit import bot
from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from subedit.database.database import getLanguageCode, updateLanguageCode
from subedit.helpers.Filters.custom_filters import CallbackButtonDataFilter
from subedit.plugins.editor.line_pagination import paginateLine
from subedit.plugins.editor.sub_editor import fetchLine
from easygoogletranslate import EasyGoogleTranslate


@bot.on_callback_query(CallbackButtonDataFilter("TRANSLATE"))
async def translateMenu(_, query):
    chat_id = query.from_user.id
    message_id = query.message.id
    subtitle_id = query.data.split("|")[1]
    index = int(query.data.split("|")[2])
    language_code = await getLanguageCode(chat_id)

    await bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=f"Translate the line to {language_code}",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="👨🏽‍💻 Translate",
                        callback_data=f"TRANSLATE_LINE|{subtitle_id}|{index}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🌐 Language",
                        callback_data=f"TRANSLATE_LANGUAGE|{subtitle_id}|{index}"
                    ),
                    InlineKeyboardButton(
                        text="❎ Cancel",
                        callback_data=f"CANCEL_TRANSLATION|{subtitle_id}|{index}"
                    )
                ]
            ]
        )
    )


@bot.on_callback_query(CallbackButtonDataFilter("TRANSLATE_LANGUAGE"))
async def translateLanguage(_, query):
    chat_id = query.from_user.id
    message_id = query.message.id
    subtitle_id = query.data.split("|")[1]
    index = int(query.data.split("|")[2])
    language_code = await getLanguageCode(chat_id)

    await bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=f"Current target language is **{language_code}**\nSend the language code for the target language.\n\nExample:\nSend `en` for English\nSend `ml` for Malayalam\n\nSend `hi` for Hindi.\n\nIf you don't know your code, check it [HERE](https://en.wikipedia.org/wiki/List_of_ISO_639_language_codes).",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="👨🏽‍💻 Send Code",
                        callback_data=f"TRANSLATE_CODE_SEND|{subtitle_id}|{index}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="❎ Cancel",
                        callback_data=f"CANCEL_TRANSLATION|{subtitle_id}|{index}"
                    )
                ]
            ]
        )
    )


@bot.on_callback_query(CallbackButtonDataFilter("TRANSLATE_CODE_SEND"))
async def translateLanguageSend(_, query):
    chat_id = query.from_user.id
    message_id = query.message.id
    subtitle_id = query.data.split("|")[1]
    index = int(query.data.split("|")[2])

    msg = await bot.send_message(
        chat_id=chat_id,
        text=f"Send the code..."
    )
    try:
        response = await bot.listen.Message(
            filters.text, filters.user(chat_id), timeout=120
        )
    except asyncio.TimeoutError:
        await paginateLine(query)
        return

    if response:
        language_code = response.text.lower()
        await updateLanguageCode(chat_id, language_code)
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=f"Translate the line to {language_code}",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="👨🏽‍💻 Translate",
                            callback_data=f"TRANSLATE_LINE|{subtitle_id}|{index}"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="🌐 Language",
                            callback_data=f"TRANSLATE_LANGUAGE|{subtitle_id}|{index}"
                        ),
                        InlineKeyboardButton(
                            text="❎ Cancel",
                            callback_data=f"CANCEL_TRANSLATION|{subtitle_id}|{index}"
                        )
                    ]
                ]
            )
        )
        await response.delete()
        await msg.delete()

    await bot.listen.Cancel(filters.user(chat_id))


@bot.on_callback_query(CallbackButtonDataFilter("TRANSLATE_LINE"))
async def translateLanguageSend(_, query):
    chat_id = query.from_user.id
    message_id = query.message.id
    subtitle_id = query.data.split("|")[1]
    index = int(query.data.split("|")[2])
    language_code = await getLanguageCode(chat_id)
    line = await fetchLine(subtitle_id, index)
    if line:
        translated_line = EasyGoogleTranslate().translate(line["original"], target_language=language_code)
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=f"Click on the text to copy.\n\n__Original:__\n`{line['original']}`\n\n__Translation:__\n`{translated_line}`",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="💠 Translate Menu",
                            callback_data=f"TRANSLATE|{subtitle_id}|{index}"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="⬅️ Editor",
                            callback_data=f"CANCEL_TRANSLATION|{subtitle_id}|{index}"
                        )
                    ]
                ]
            )
        )


@bot.on_callback_query(CallbackButtonDataFilter("CANCEL_TRANSLATION"))
async def translateCancel(_, query):
    await paginateLine(query)
