from pyrogram import filters
from subedit.database.database import getSubtitleID, getLastMessageID
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from subedit import bot

edit_cmd_button = [
    [InlineKeyboardButton("📖 Start New", callback_data="START_NEW_BUTTON")]
]


@bot.on_message(filters.command(["edit"]))
async def Editor(_, message: Message):
    sub_ids = await getSubtitleID(message.from_user)
    print(sub_ids)
    if not sub_ids:
        await message.reply_text(
            "You don't have any subtitles to edit. Start a new one by clicking below",
            reply_markup=InlineKeyboardMarkup(edit_cmd_button),
        )
    else:
        edit_subID_button = []
        for ID in sub_ids:
            print(ID)
            button_data = f"EDIT_SUB_MENU|{ID['id']}"
            print(button_data)
            edit_subID_button.append(
                [InlineKeyboardButton(f"{ID['file_name']}", callback_data=button_data)],
            )
        edit_subID_button.append(
            [InlineKeyboardButton("📖 Start New", callback_data="START_NEW_BUTTON")]
        )
        await message.reply_text(
            "Choose a subtitle to edit or start new",
            reply_markup=InlineKeyboardMarkup(edit_subID_button),
        )
