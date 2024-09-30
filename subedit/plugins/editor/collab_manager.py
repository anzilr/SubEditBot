from urllib.parse import quote

from pyrogram import filters
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from subedit import bot
from subedit.database.database import updateCollabID, getSubtitleName, updateCollabStatus, getCollabStatus, \
    getCollabAdmin, updateCollabMember, getCollabMembers, removeUserFromCollab, checkCollabMember, removeCollabData, \
    getCollabMember, getCollabBlacklist, updateCollabBlacklist, removeCollabBlacklistUser, checkCollabMemberBlacklist
from subedit.helpers.Filters.custom_filters import collab_filter, CallbackButtonDataFilter


@bot.on_message(filters.create(collab_filter))
async def add_collaborator(client, message):
    user_id = message.from_user.id
    subtitle_id = message.text.split()[1]
    if await checkCollabMemberBlacklist(subtitle_id, user_id):
        await message.reply(text="You are blacklisted from collaborating on this subtitle.")
        return
    username = message.from_user.username
    if not username:
        username = message.from_user.first_name

    # Extract the number from the message
    user_data = {"id": str(user_id), "username": username}
    if not await getCollabStatus(subtitle_id):
        await message.reply(text="This subtitle is not in collab mode.")
        return
    if await checkCollabMember(subtitle_id, user_id):
        await message.reply(text="You are already a collaborator on this subtitle.")
        return
    file_name = await getSubtitleName(subtitle_id)
    sub_data = {"id": subtitle_id, "file_name": file_name, "collab": "member"}
    await updateCollabID(user_id, sub_data)
    await updateCollabMember(subtitle_id, user_data)
    await message.reply(
        text="The subtitle has been linked to your account. You can now start editing and collaborating on this subtitle.",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text=f"{file_name}", callback_data=f"MAIN_MENU|{subtitle_id}")
                        ]
                ]
        )
    )


@bot.on_callback_query(CallbackButtonDataFilter("START_COLLAB"))
async def start_collab_menu(_, query: CallbackQuery):
    user_id = query.from_user.id
    subtitle_id = query.data.split("|")[1]
    await bot.edit_message_text(
        chat_id=user_id,
        message_id=query.message.id,
        text="Do you want to turn on collab mode on this subtitle?",
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(text="✅ Yes", callback_data=f"START_COLLAB_CONFIRM|{subtitle_id}")],
                [InlineKeyboardButton(text="❎ No", callback_data=f"COLLAB_MENU|{subtitle_id}")]
            ]
        )
    )


@bot.on_callback_query(CallbackButtonDataFilter("START_COLLAB_CONFIRM"))
async def start_collab(_, query: CallbackQuery):
    user_id = query.from_user.id
    subtitle_id = query.data.split("|")[1]
    await updateCollabStatus(subtitle_id, True, user_id)
    username = query.from_user.username
    if not username:
        username = query.from_user.first_name
    user_data = {"id": str(user_id), "username": username}
    await updateCollabMember(subtitle_id, user_data)
    await bot.send_message(chat_id=user_id,
        text=f"You've turned on collab mode on this subtitle. Share the following command with your collaborators to add them:\n\n`/collab {subtitle_id}`",
                       reply_markup=InlineKeyboardMarkup(
                           [
                               [
                                   InlineKeyboardButton(text="⤴️ Share", url='t.me/share/url?url=' + quote(f"Send the following command to @SubEditBot to start collaborating:\n\n`/collab {subtitle_id}`"))
                               ],
                               [
                                   InlineKeyboardButton(text="💠 Menu",
                                                        callback_data=f"MAIN_MENU|{subtitle_id}")
                               ]
                           ]
                       )
                           )


@bot.on_callback_query(CallbackButtonDataFilter("STOP_COLLAB"))
async def stop_collab_menu(_, query: CallbackQuery):
    user_id = query.from_user.id
    subtitle_id = query.data.split("|")[1]
    await bot.edit_message_text(
        chat_id=user_id,
        message_id=query.message.id,
        text="Do you want to turn off collab mode on this subtitle? It will remove all collaborators.",
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(text="✅ Yes", callback_data=f"STOP_COLLAB_CONFIRM|{subtitle_id}")],
                [InlineKeyboardButton(text="❎ No", callback_data=f"COLLAB_MENU|{subtitle_id}")]
            ]
        )
    )


@bot.on_callback_query(CallbackButtonDataFilter("STOP_COLLAB_CONFIRM"))
async def stop_collab(_, query: CallbackQuery):
    user_id = query.from_user.id
    subtitle_id = query.data.split("|")[1]
    await removeCollabData(subtitle_id)
    await bot.send_message(
        chat_id=user_id,
        text="Collab mode has been disabled on this subtitle.",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text="💠 Menu", callback_data=f"MAIN_MENU|{subtitle_id}")
                ]
            ]
        )
    )


@bot.on_callback_query(CallbackButtonDataFilter("COLLAB_MENU"))
async def collab_menu(_, query: CallbackQuery):
    user_id = query.from_user.id
    subtitle_id = query.data.split("|")[1]
    collab_status = await getCollabStatus(subtitle_id)
    if collab_status and await getCollabAdmin(subtitle_id) == user_id:
        collab_members = await getCollabMembers(subtitle_id)
        members_list = "\n".join([f"@{m['username']} (ID: {m['id']})" for m in collab_members])
        await bot.edit_message_text(
            chat_id=user_id,
            message_id=query.message.id,
            text=f"You've turned on collab mode on this subtitle. Share the following command with your collaborators to add them:\n\n`/collab {subtitle_id}`\n\nActive collaborators:\n\n{members_list}",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text="📥 Update Collaborators",
                                             callback_data=f"UPDATE_COLLABORATES|{subtitle_id}")
                    ],
                    [
                        InlineKeyboardButton(text="⏹ Stop Collaboration", callback_data=f"STOP_COLLAB|{subtitle_id}")
                    ],
                    [
                        InlineKeyboardButton(text="💠 Menu",
                                             callback_data=f"MAIN_MENU|{subtitle_id}")
                    ]
                ]
            )
        )

    elif await checkCollabMember(subtitle_id, user_id):
        await bot.edit_message_text(
            chat_id=user_id,
            message_id=query.message.id,
            text=f"You are a collaborator on this subtitle. You can start editing and collaborating on this subtitle.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text="⏹ Stop Collaboration",
                                             callback_data=f"STOP_COLLABORATING|{subtitle_id}")
                    ],
                    [
                        InlineKeyboardButton(text="💠 Menu",
                                             callback_data=f"MAIN_MENU|{subtitle_id}")
                    ]
                ]
            )
        )

    elif await getCollabAdmin(subtitle_id) == user_id:
        await bot.edit_message_text(
            chat_id=user_id,
            message_id=query.message.id,
            text="The collaborative editing feature in SubEditBot allows multiple users to work together on editing subtitles. Authorized collaborators can access and modify subtitles in real-time, while administrators or original owners of the subtitle can manage permissions, such as blacklisting or removing collaborators. This feature enhances teamwork, ensuring efficient collaboration by allowing users to contribute, edit, or review subtitle files collectively within the bot’s interface.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text="▶️ Start Collaboration", callback_data=f"START_COLLAB|{subtitle_id}")
                    ],
                    [
                        InlineKeyboardButton(text="💠 Menu",
                                             callback_data=f"MAIN_MENU|{subtitle_id}")
                    ]
                ]
            )
        )


@bot.on_callback_query(CallbackButtonDataFilter("STOP_COLLABORATING"))
async def stop_collab_member_menu(_, query: CallbackQuery):
    user_id = query.from_user.id
    subtitle_id = query.data.split("|")[1]
    await bot.edit_message_text(
        chat_id=user_id,
        message_id=query.message.id,
        text="Do you want to leave from this subtitle's collaboration?",
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(text="✅ Yes", callback_data=f"STOP_COLLABORATING_CONFIRM|{subtitle_id}")],
                [InlineKeyboardButton(text="❎ No", callback_data=f"COLLAB_MENU|{subtitle_id}")]
            ]
        )
    )


@bot.on_callback_query(CallbackButtonDataFilter("STOP_COLLABORATING_CONFIRM"))
async def stop_collab_member(_, query: CallbackQuery):
    user_id = query.from_user.id
    subtitle_id = query.data.split("|")[1]
    await removeUserFromCollab(user_id, subtitle_id)
    await bot.edit_message_text(
        chat_id=user_id,
        message_id=query.message.id,
        text=f"You left from this subtitle's collaboration.",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text="💠 Menu", callback_data=f"MAIN_MENU|{subtitle_id}")
                ]
            ]
        )
    )


@bot.on_callback_query(CallbackButtonDataFilter("UPDATE_COLLABORATES"))
async def update_collab_member_menu(_, query: CallbackQuery):
    user_id = query.from_user.id
    subtitle_id = query.data.split("|")[1]
    collab_members = await getCollabMembers(subtitle_id)
    members_list = "\n".join([f"@{m['username']} (ID: {m['id']})" for m in collab_members])
    await bot.edit_message_text(
        chat_id=user_id,
        message_id=query.message.id,
        text=f"Active collaborators:\n{members_list}",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text="🔗 Add Collaborator",
                                             callback_data=f"ADD_COLLABORATOR|{subtitle_id}")
                ],
                [
                    InlineKeyboardButton(text="🔫 Remove Collaborator",
                                             callback_data=f"REMOVE_COLLABORATOR|{subtitle_id}")
                ],
                [
                    InlineKeyboardButton(text="☠️ Blacklist Collaborator",
                                         callback_data=f"BLKLST_CLB_MENU|{subtitle_id}")
                ],
                [
                    InlineKeyboardButton(text="💠 Menu",
                                             callback_data=f"MAIN_MENU|{subtitle_id}")
                ]
            ]
        )
    )


@bot.on_callback_query(CallbackButtonDataFilter("ADD_COLLABORATOR"))
async def add_collaborator_menu(_, query: CallbackQuery):
    user_id = query.from_user.id
    subtitle_id = query.data.split("|")[1]
    await bot.edit_message_text(
        chat_id=user_id,
        message_id=query.message.id,
        text=f"Share the following command with your collaborators to add them:\n\n`/collab {subtitle_id}`",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text="⤴️ Share", url='t.me/share/url?url=' + quote(
                        f"Send the following command to @SubEditBot to start collaborating:\n\n`/collab {subtitle_id}`"))
                ],
                [
                    InlineKeyboardButton(text="💠 Menu",
                                         callback_data=f"MAIN_MENU|{subtitle_id}")
                ]
            ]
        )
    )


@bot.on_callback_query(CallbackButtonDataFilter("REMOVE_COLLABORATOR"))
async def remove_collaborator_menu(_, query: CallbackQuery):
    user_id = query.from_user.id
    subtitle_id = query.data.split("|")[1]
    collab_members = await getCollabMembers(subtitle_id)
    members_list = [
        [InlineKeyboardButton(
            f"@{m['username']} (ID: {m['id']})",
            callback_data=f"RMV_CLB_MBR|{subtitle_id}|{m['id']}"
        )]
        for m in collab_members
    ]

    members_list.append([InlineKeyboardButton(text="💠 Menu", callback_data=f"MAIN_MENU|{subtitle_id}")])
    await bot.edit_message_text(
        chat_id=user_id,
        message_id=query.message.id,
        text=f"Select a collaborator to remove:",
        reply_markup=InlineKeyboardMarkup(members_list)
    )


@bot.on_callback_query(CallbackButtonDataFilter("RMV_CLB_MBR"))
async def remove_collaborator(_, query: CallbackQuery):
    user_id = query.from_user.id
    subtitle_id = query.data.split("|")[1]
    user_id_to_remove = query.data.split("|")[-1]
    user_data = await getCollabMember(subtitle_id, user_id_to_remove)
    username = user_data['username']
    await removeUserFromCollab(user_id_to_remove, subtitle_id)
    await bot.edit_message_text(
        chat_id=user_id,
        message_id=query.message.id,
        text=f"You've removed @{username} from this subtitle's collaborators.",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text="💠 Menu", callback_data=f"MAIN_MENU|{subtitle_id}")
                ]
            ]
        )
    )


@bot.on_callback_query(CallbackButtonDataFilter("BLKLST_CLB_MENU"))
async def blacklist_collaborator_menu_button(_, query: CallbackQuery):
    await blacklist_collaborator_menu(query)


@bot.on_callback_query(CallbackButtonDataFilter("BLKLST_CLB_MBR"))
async def blacklist_collaborator(_, query: CallbackQuery):
    subtitle_id = query.data.split("|")[1]
    user_id_to_blacklist = str(query.data.split("|")[-1])
    user_data = await getCollabMember(subtitle_id, user_id_to_blacklist)
    await updateCollabBlacklist(subtitle_id, user_data)
    await blacklist_collaborator_menu(query)
    await query.answer(text="☠️ Collaborator blacklisted.")


@bot.on_callback_query(CallbackButtonDataFilter("UBLK_CLB_MBR"))
async def unblacklist_collaborator(_, query: CallbackQuery):
    subtitle_id = query.data.split("|")[1]
    user_id_to_unblacklist = str(query.data.split("|")[-1])
    await removeCollabBlacklistUser(subtitle_id, user_id_to_unblacklist)
    await blacklist_collaborator_menu(query)
    await query.answer(text="👤 Collaborator Whitelisted.")


async def blacklist_collaborator_menu(query):
    user_id = query.from_user.id
    subtitle_id = query.data.split("|")[1]
    # Fetch collaborators and blacklist
    collab_members = await getCollabMembers(subtitle_id)
    blacklist_collabor = await getCollabBlacklist(subtitle_id)

    # Ensure blacklist_collabor is initialized
    if blacklist_collabor is None:
        blacklist_collabor = []

    # Combine collab_members and blacklist_collabor, avoiding duplicates
    all_members = {m['id']: m for m in collab_members}  # Use dict to avoid duplicates
    for m in blacklist_collabor:
        all_members[m['id']] = m  # Add/overwrite with blacklist collaborators

    # Convert back to list to process
    merged_members = list(all_members.values())

    # Extract IDs of blacklisted collaborators
    blacklist_ids = [m['id'] for m in blacklist_collabor]

    # Build the inline keyboard list
    members_list = []
    for m in merged_members:
        if m['id'] not in blacklist_ids:  # If not blacklisted
            members_list.append([InlineKeyboardButton(
                f"👤 @{m['username']} (ID: {m['id']})",
                callback_data=f"BLKLST_CLB_MBR|{subtitle_id}|{m['id']}"
            )])
        else:  # If blacklisted
            members_list.append([InlineKeyboardButton(
                f"☠️ @{m['username']} (ID: {m['id']})",
                callback_data=f"UBLK_CLB_MBR|{subtitle_id}|{m['id']}"
            )])

    members_list.append([InlineKeyboardButton(text="👫 Collaborate", callback_data=f"COLLAB_MENU|{subtitle_id}")])
    await bot.edit_message_text(
        chat_id=user_id,
        message_id=query.message.id,
        text=f"Select a collaborator to blacklist or whitelist:",
        reply_markup=InlineKeyboardMarkup(members_list)
    )
