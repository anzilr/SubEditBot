from pyrogram import filters
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from subedit import bot
from subedit.helpers.start_constants import *
from subedit.config import OWNER_USERID, SUDO_USERID
from subedit.database import database

START_BUTTON = [
    [
        InlineKeyboardButton("📖 Commands", callback_data="COMMAND_BUTTON"),
        InlineKeyboardButton("👨‍💻 About me", callback_data="ABOUT_BUTTON"),
    ],
    [
        InlineKeyboardButton(
            "🔭 Source",
            url="https://github.com/sanjit-sinha/TelegramBot-Boilerplate",
        )
    ],
]

COMMAND_BUTTON = [
    [
        InlineKeyboardButton("Users", callback_data="USER_BUTTON"),
        InlineKeyboardButton("Sudo", callback_data="SUDO_BUTTON"),
    ],
    [InlineKeyboardButton("Developer", callback_data="DEV_BUTTON")],
    [InlineKeyboardButton("🔙 Go Back", callback_data="START_BUTTON")],
]

GOBACK_1_BUTTON = [[InlineKeyboardButton("🔙 Go Back", callback_data="START_BUTTON")]]
GOBACK_2_BUTTON = [[InlineKeyboardButton("🔙 Go Back", callback_data="COMMAND_BUTTON")]]


@bot.on_message(filters.command(["start", "help"]))
async def start(_, message: Message):
    await database.saveUser(message.from_user)
    await message.reply_photo(
        photo="https://imgur.com/kmoXW3U"

    )
    return await message.reply_text(
        START_CAPTION, reply_markup=InlineKeyboardMarkup(START_BUTTON), quote=True

    )


@bot.on_callback_query(filters.regex("_BUTTON"))
async def botCallbacks(_, CallbackQuery: CallbackQuery):
    clicker_user_id = CallbackQuery.from_user.id
    user_id = CallbackQuery.message.reply_to_message.from_user.id

    if clicker_user_id != user_id:
        return await CallbackQuery.answer("This command is not initiated by you.")

    if CallbackQuery.data == "SUDO_BUTTON":
        if clicker_user_id not in SUDO_USERID:
            return await CallbackQuery.answer(
                "You are not in the sudo user list.", show_alert=True
            )
        await CallbackQuery.edit_message_text(
            SUDO_TEXT, reply_markup=InlineKeyboardMarkup(GOBACK_2_BUTTON)
        )

    elif CallbackQuery.data == "DEV_BUTTON":
        if clicker_user_id not in OWNER_USERID:
            return await CallbackQuery.answer(
                "This is developer restricted command.", show_alert=True
            )
        await CallbackQuery.edit_message_text(
            DEV_TEXT, reply_markup=InlineKeyboardMarkup(GOBACK_2_BUTTON)
        )

    if CallbackQuery.data == "ABOUT_BUTTON":
        await CallbackQuery.edit_message_text(
            ABOUT_CAPTION, reply_markup=InlineKeyboardMarkup(GOBACK_1_BUTTON)
        )

    elif CallbackQuery.data == "START_BUTTON":
        await CallbackQuery.edit_message_text(
            START_CAPTION, reply_markup=InlineKeyboardMarkup(START_BUTTON)
        )

    elif CallbackQuery.data == "COMMAND_BUTTON":
        await CallbackQuery.edit_message_text(
            COMMAND_CAPTION, reply_markup=InlineKeyboardMarkup(COMMAND_BUTTON)
        )

    elif CallbackQuery.data == "USER_BUTTON":
        await CallbackQuery.edit_message_text(
            USER_TEXT, reply_markup=InlineKeyboardMarkup(GOBACK_2_BUTTON)
        )
    await CallbackQuery.answer()
