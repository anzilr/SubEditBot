from subedit import bot
from subedit.database.database import deleteSubtitleDocument, getSubtitleID
from subedit.helpers.Filters.custom_filters import CallbackButtonDataFilter
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup


@bot.on_callback_query(CallbackButtonDataFilter("DELETE_SUB"))
async def deleteSubtitle(_, query):
    sub_id = query.data.split("|")[1]
    user_id = query.from_user.id
    await bot.edit_message_text(
        chat_id=user_id,
        message_id=query.message.id,
        text="Deleting the subtitle will erase all the data from this session. Make sure you compiled the work before deleting.",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Delete",
                        callback_data=f"DELETE_CURRENT_SUB|{sub_id}",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="Cancel",
                        callback_data=f"CANCEL_DELETE_SUB|{sub_id}",
                    )
                ],
            ]
        ),
    )


@bot.on_callback_query(CallbackButtonDataFilter("DELETE_CURRENT_SUB"))
async def deleteSubtitleConfirm(_, query):
    sub_id = query.data.split("|")[1]
    user_id = query.from_user.id
    await deleteSubtitleDocument(user_id, sub_id)
    sub_ids = await getSubtitleID(query.from_user)
    if not sub_ids:
        await bot.edit_message_text(
            chat_id=user_id,
            message_id=query.message.id,
            text="You don't have any subtitles to edit. Start a new one by clicking below",
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
    else:
        edit_subID_button = []
        for ID in sub_ids:
            button_data = f"MAIN_MENU|{ID['id']}"
            edit_subID_button.append(
                [InlineKeyboardButton(f"{ID['file_name']}", callback_data=button_data)],
            )
        edit_subID_button.append(
            [InlineKeyboardButton("📖 Start New", callback_data="START_NEW_BUTTON")]
        )
        await bot.edit_message_text(
            chat_id=user_id,
            message_id=query.message.id,
            text="Choose a subtitle to edit or start new",
            reply_markup=InlineKeyboardMarkup(edit_subID_button),
        )


@bot.on_callback_query(CallbackButtonDataFilter("CANCEL_DELETE_SUB"))
async def cancelDeleteSub(_, query):
    sub_id = query.data.split("|")[1]
    user_id = query.from_user.id
    sub_ids = await getSubtitleID(query.from_user)
    if not sub_ids:
        await bot.edit_message_text(
            chat_id=user_id,
            message_id=query.message.id,
            text="You don't have any subtitles to edit. Start a new one by clicking below",
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
    else:
        edit_subID_button = []
        for ID in sub_ids:
            button_data = f"MAIN_MENU|{ID['id']}"
            edit_subID_button.append(
                [InlineKeyboardButton(f"{ID['file_name']}", callback_data=button_data)],
            )
        edit_subID_button.append(
            [InlineKeyboardButton("📖 Start New", callback_data="START_NEW_BUTTON")]
        )
        await bot.edit_message_text(
            chat_id=user_id,
            message_id=query.message.id,
            text="Choose a subtitle to edit or start new",
            reply_markup=InlineKeyboardMarkup(edit_subID_button),
        )
