from pyrogram import filters
from subedit.database.database import getSubtitleID, getLastMessageID
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from subedit import bot

edit_cmd_button = [
    [InlineKeyboardButton("📖 Start New", callback_data="START_NEW_BUTTON")]
]


@bot.on_message(filters.command(["edit"]))
async def editMenu(_, message):
    user_id = message.from_user.id
    message_id = message.id
    await Editor(user_id, message_id)


async def Editor(user_id, message_id):
    sub_ids = await getSubtitleID(user_id)
    # print(sub_ids)
    if not sub_ids:
        await bot.send_message(
            chat_id=user_id,
            text="You don't have any subtitles to edit. Start a new one by clicking below",
            reply_to_message_id=message_id,
            reply_markup=InlineKeyboardMarkup(edit_cmd_button),
        )
    else:
        edit_subID_button = []
        for ID in sub_ids:
            # print(ID)
            button_data = f"MAIN_MENU|{ID['id']}"
            # print(button_data)
            edit_subID_button.append(
                [InlineKeyboardButton(f"{ID['file_name']}", callback_data=button_data)],
            )
        edit_subID_button.append(
            [InlineKeyboardButton("📖 Start New", callback_data="START_NEW_BUTTON")]
        )
        await bot.send_message(
            chat_id=user_id,
            reply_to_message_id=message_id,
            text="Choose a subtitle to edit or start new",
            reply_markup=InlineKeyboardMarkup(edit_subID_button),
        )
