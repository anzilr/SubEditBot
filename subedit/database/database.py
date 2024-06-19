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
        "subtitles": [],
    }
    await db.create_user(insert_format)


async def updateSubtitleID(user_id, sub_data):
    """
    Update the user's subtitles list with the new sub_id.
    """
    await db.add_sub_id(user_id, sub_data)


async def getSubtitleID(user_id):
    """
    Get the user's sub_id.
    """
    return await db.get_sub_id(user_id)


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


async def getLastMessageID(subtitle_id):
    message_id = await db.get_last_message_id(subtitle_id)
    return message_id


async def updateSubtitleEdited(subtitle_id, index, edited_text):
    await db.update_subtitle_edited(subtitle_id, index, edited_text)


async def updateNewTime(subtitle_id, index, start, end):
    await db.update_new_time(subtitle_id, index, start, end)
