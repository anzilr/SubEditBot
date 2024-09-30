from subedit.database.MongoDb import db
from datetime import datetime, timezone


async def saveUser(user):
    """
    Save the new user id in the database if it is not already there.
    """

    insert_format = {
        "_id": user.id,
        "name": (user.first_name or " ") + (user.last_name or ""),
        "username": user.username,
        "date": datetime.now(timezone.utc),
        "language_code": "en",
        "subtitles": [],
    }
    await db.create_user(insert_format)


async def updateSubtitleID(user_id, sub_data):
    """
    Update the user's subtitles list with the new sub_id.
    """
    await db.add_sub_id(user_id, sub_data)


async def updateCollabID(user_id, collab_data):
    await db.add_collab_id(user_id, collab_data)


async def updateCollabStatus(subtitle_id, status, user_id):
    await db.update_collab_status(subtitle_id, status, user_id)


async def getCollabStatus(subtitle_id):
    return await db.get_collab_status(subtitle_id)


async def getCollabAdmin(subtitle_id):
    return await db.get_collab_admin(subtitle_id)


async def updateCollabMember(subtitle_id, user_data):
    await db.update_collab_members(subtitle_id, user_data)


async def getCollabMembers(subtitle_id):
    return await db.get_collab_members(subtitle_id)


async def getCollabMember(subtitle_id, user_id):
    return await db.get_collab_member(subtitle_id, user_id)


async def checkCollabMember(subtitle_id, user_id):
    return await db.is_collab_member(subtitle_id, user_id)


async def removeUserFromCollab(user_id, subtitle_id):
    await db.remove_collab_member(subtitle_id, user_id)
    await db.remove_subtitle_from_user(int(user_id), subtitle_id)


async def removeCollabData(subtitle_id):
    users = await db.get_collab_members(subtitle_id)
    collab_admin = await db.get_collab_admin(subtitle_id)
    # print(collab_admin)
    if users:
        for user in users:
            user_id = str(user["id"])
            await removeUserFromCollab(user_id, subtitle_id)
            if user_id != str(collab_admin):
                await db.remove_subtitle_from_user(int(user_id), subtitle_id)
    await db.remove_collab_data(subtitle_id)


async def updateCollabBlacklist(subtitle_id, user_data):
    await db.update_collab_blacklist(subtitle_id, user_data)


async def getCollabBlacklist(subtitle_id):
    return await db.get_collab_blacklist(subtitle_id)


async def removeCollabBlacklistUser(subtitle_id, user_id):
    await db.remove_collab_blacklist_user(subtitle_id, user_id)


async def getCollabBlacklistUser(subtitle_id, user_id):
    return await db.get_collab_blacklist_user(subtitle_id, user_id)


async def checkCollabMemberBlacklist(subtitle_id, user_id):
    return await db.is_collab_member_blacklist(subtitle_id, user_id)


async def getSubtitleID(user_id):
    """
    Get the user's sub_id.
    """
    return await db.get_sub_id(user_id)

async def getSubtitleName(subtitle_id):
    return await db.get_sub_name(subtitle_id)


# create new document with the parsed data
async def createSubtitleDocument(sub_document):
    await db.create_subtitle(sub_document)
    print("Uploaded subtitle contents")


async def getSubtitleDocument(subtitle_id):
    return await db.read_subtitle(subtitle_id)


async def deleteSubtitleDocument(user_id, subtitle_id):
    await db.delete_subtitle(subtitle_id)
    await db.remove_subtitle_from_user(user_id, subtitle_id)


async def UpdateSubtitleArray(subtitle_id, subtitles):
    return await db.update_subtitle_array(subtitle_id, subtitles)


async def getSubtitleArray(subtitle_id):
    return await db.get_subtitles_array(subtitle_id)


async def getSubtitleLines(subtitle_id, offset):
    result = await db.fetch_subtitles_by_offset(subtitle_id, offset)
    # print(result)
    return result


async def getSubtitleByIndex(subtitle_id, index):
    result = await db.fetch_subtitle_by_index(subtitle_id, index)
    # print(result)
    return result


async def updateLastMessageID(subtitle_id, message_id):
    await db.update_last_message_id(subtitle_id, message_id)


async def updateLastIndex(subtitle_id, index):
    await db.update_last_edited_line(subtitle_id, index)


async def updateLastIndexAndMessageID(subtitle_id, index, message_id):
    await db.update_last_index_and_message_id(subtitle_id, index, message_id)


async def getLastIndexAndMessageID(subtitle_id):
    index, message_id = await db.get_last_message_id_and_index(subtitle_id)
    return index, message_id


async def getLastIndexAndMessageIDCollabStatus(subtitle_id):
    index, message_id, collab_status = await db.get_last_message_id_index_and_collab_status(subtitle_id)
    return index, message_id, collab_status


async def getLastMessageID(subtitle_id):
    message_id = await db.get_last_message_id(subtitle_id)
    return message_id


async def updateSubtitleEdited(subtitle_id, index, edited_text):
    await db.update_subtitle_edited(subtitle_id, index, edited_text)


async def updateNewTime(subtitle_id, index, start, end):
    await db.update_new_time(subtitle_id, index, start, end)


async def updateLanguageCode(user_id, language_code):
    await db.update_language_code(user_id, language_code)


async def getLanguageCode(user_id):
    language_code = await db.get_language_code(user_id)
    return language_code
