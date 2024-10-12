from pymongo.errors import ServerSelectionTimeoutError, DuplicateKeyError
from pyrogram.filters import document

from subedit.config import MONGO_URI, DB_NAME
from subedit.logging import LOGGER
import motor.motor_asyncio


class MongoDB:
    def __init__(self, uri=MONGO_URI, db_name=DB_NAME):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self.client[db_name]
        self.subtitles_collection = self.db.subtitles
        self.users_collection = self.db.users

    # CRUD operations for 'subtitles' collection
    async def create_subtitle(self, subtitle_data):
        result = await self.subtitles_collection.insert_one(subtitle_data)
        return result.inserted_id

    async def read_subtitle(self, subtitle_id):
        subtitle = await self.subtitles_collection.find_one({"_id": subtitle_id})
        return subtitle

    async def update_subtitle(self, subtitle_id, update_data):
        result = await self.subtitles_collection.update_one(
            {"_id": subtitle_id}, {"$set": update_data}
        )
        return result.modified_count

    async def delete_subtitle(self, subtitle_id):
        result = await self.subtitles_collection.delete_one({"_id": subtitle_id})
        return result.deleted_count

    # Add object to subtitles array
    async def add_to_subtitles_array(self, document_id, subtitle_obj):
        result = await self.subtitles_collection.update_one(
            {"_id": document_id}, {"$push": {"subtitles": subtitle_obj}}
        )
        return result.modified_count

    # Read the subtitles array from a document
    async def get_subtitles_array(self, document_id):
        document = await self.subtitles_collection.find_one(
            {"_id": document_id},
            {
                "subtitles": 1,
                "_id": 0,
            },  # Projecting to only include the subtitles array
        )
        result = document.get("subtitles") if document else None
        return result

    async def fetch_subtitle_by_index(self, subtitle_id, index):
        # Find the first matching subtitle in the subtitles array of the document with the given id and index.
        document = await self.subtitles_collection.find_one(
            {"_id": subtitle_id, "subtitles.index": index},
            {"subtitles": {"$elemMatch": {"index": index}}, "_id": 0},
        )
        if document and "subtitles" in document:
            return document["subtitles"][0]  # Return the first matching subtitle
        return None

    async def fetch_subtitles_by_offset(self, subtitle_id, offset):
        limit = 50
        document = await self.subtitles_collection.find_one(
            {"_id": subtitle_id},
            {
                "subtitles": {"$slice": [offset, limit]},
                "_id": 0,
            },  # Offset by 99 and limit to 99
        )
        return document.get("subtitles") if document else None

    async def update_subtitle_edited(self, subtitle_id, index, edited_text):
        result = await self.subtitles_collection.update_one(
            {"_id": subtitle_id, "subtitles.index": index},
            {"$set": {"subtitles.$.edited": edited_text}},
        )
        return result.modified_count

    async def update_new_time(self, subtitle_id, index, start, end):
        result = await self.subtitles_collection.update_one(
            {"_id": subtitle_id, "subtitles.index": index},
            {"$set": {"subtitles.$.start_time": start, "subtitles.$.end_time": end}},
        )
        return result.modified_count

    async def add_sub_id(self, user_id, sub_data):
        result = await self.users_collection.update_one(
            {"_id": user_id}, {"$push": {"subtitles": sub_data}}
        )
        return result.modified_count

    async def add_collab_id(self, user_id, collab_data):
        result = await self.users_collection.update_one(
            {"_id": user_id}, {"$push": {"subtitles": collab_data}}
        )

    async def get_sub_id(self, user_id):
        document = await self.users_collection.find_one(
            {"_id": user_id},
            {
                "subtitles": 1,
                "_id": 0,
            },  # Projecting to only include the subtitles array
        )
        return document.get("subtitles") if document else None

    async def get_sub_name(self, subtitle_id):
        document = await self.subtitles_collection.find_one(
            {"_id": subtitle_id},
            {"file_name": 1, "_id": 0}
        )
        return document.get("file_name") if document else None

    async def update_last_message_id(self, subtitle_id, message_id):
        result = await self.subtitles_collection.update_one(
            {"_id": subtitle_id}, {"$set": {"last_message_id": message_id}}
        )
        return result.modified_count

    async def update_last_index_and_message_id(self, subtitle_id, index, message_id):
        result = await self.subtitles_collection.update_one(
            {"_id": subtitle_id},
            {"$set": {"last_message_id": message_id, "last_edited_line": index}},
        )
        return result.modified_count

    async def update_collab_status(self, subtitle_id, status, user_id):
        result = await self.subtitles_collection.update_one(
            {"_id": subtitle_id},
            {"$set": {"collab_status": status, "collab_admin": user_id}},
        )
        return result.modified_count > 0

    async def get_collab_status(self, subtitle_id):
        document = await self.subtitles_collection.find_one(
            {"_id": subtitle_id},
            {"collab_status": 1, "_id": 0}
        )
        return document.get("collab_status") if document else None

    async def get_collab_admin(self, subtitle_id):
        document = await self.subtitles_collection.find_one(
            {"_id": subtitle_id},
            {"collab_admin": 1, "_id": 0}
        )
        return document.get("collab_admin") if document else None

    async def update_collab_members(self, subtitle_id, user_data):
        result = await self.subtitles_collection.update_one(
            {"_id": subtitle_id}, {"$push": {"collab_members": user_data}},
        )
        return result.modified_count > 0

    async def get_collab_members(self, subtitle_id):
        document = await self.subtitles_collection.find_one(
            {"_id": subtitle_id},
            {"collab_members": 1, "_id": 0}
        )
        return document.get("collab_members") if document else None

    async def get_collab_member(self, subtitle_id, user_id):
        document = await self.subtitles_collection.find_one(
            {"_id": subtitle_id, "collab_members.id": str(user_id)},
            {"collab_members.$": 1, "_id": 0}
        )
        return document.get("collab_members", [{}])[0] if document else None

    async def is_collab_member(self, subtitle_id, user_id):
        document = await self.subtitles_collection.find_one(
            {"_id": subtitle_id, "collab_members.id": str(user_id)},
            {"_id": 1}  # We only need to know if the document exists
        )
        return document is not None

    async def remove_collab_member(self, subtitle_id, user_id):
        # print(str(user_id))
        result = await self.subtitles_collection.update_one(
            {"_id": subtitle_id}, {"$pull": {"collab_members": {"id": str(user_id)}}},
        )
        # print(f"Removed member with id {user_id} from subtitles collection" if result.modified_count > 0 else "No member with id {user_id} found")
        return result.modified_count > 0

    async def remove_collab_data(self, subtitle_id):

        result = await self.subtitles_collection.update_one(
            {"_id": subtitle_id}, {"$unset": {"collab_status": 1, "collab_members": 1}},
        )
        return result.modified_count > 0

    async def update_collab_blacklist(self, subtitle_id, user_data):
        result = await self.subtitles_collection.update_one(
            {"_id": subtitle_id}, {"$push": {"collab_blacklist": user_data}},
        )
        return result.modified_count > 0

    async def get_collab_blacklist(self, subtitle_id):
        document = await self.subtitles_collection.find_one(
            {"_id": subtitle_id},
            {"collab_blacklist": 1, "_id": 0}
        )
        return document.get("collab_blacklist") if document else None

    async def remove_collab_blacklist_user(self, subtitle_id, user_id):
        result = await self.subtitles_collection.update_one(
            {"_id": subtitle_id}, {"$pull": {"collab_blacklist": {"id": str(user_id)}}},
        )
        return result.modified_count > 0

    async def get_collab_blacklist_user(self, subtitle_id, user_id):
        document = await self.subtitles_collection.find_one(
            {"_id": subtitle_id, "collab_blacklist.id": str(user_id)},
            {"collab_blacklist.$": 1, "_id": 0}
        )
        return document.get("collab_blacklist", [{}])[0] if document else None

    async def is_collab_member_blacklist(self, subtitle_id, user_id):
        document = await self.subtitles_collection.find_one(
            {"_id": subtitle_id, "collab_blacklist.id": str(user_id)},
            {"_id": 1}  # We only need to know if the document exists
        )
        return document is not None

    async def update_subtitle_id(self, user_id, subtitle_id, new_subtitle_id):
        sub_document = await self.read_subtitle(subtitle_id)
        if sub_document:
            sub_document.pop("_id")
            sub_document["_id"] = new_subtitle_id
            result1 = await self.create_subtitle(sub_document)
            await self.delete_subtitle(subtitle_id)

        result2 = await self.users_collection.update_one(
            {"_id": user_id, "subtitles.id": subtitle_id},
            {"$set": {"subtitles.$.id": new_subtitle_id}}
        )
        return result2.modified_count > 0


    async def update_last_edited_line(self, subtitle_id, index):
        result = await self.subtitles_collection.update_one(
            {"_id": subtitle_id}, {"$set": {"last_edited_line": index}}
        )
        return result.modified_count > 0

    async def get_last_message_id(self, subtitle_id):
        document = await self.subtitles_collection.find_one(
            {"_id": subtitle_id}, {"last_message_id": 1, "_id": 0}
        )
        return document.get("last_message_id") if document else None

    async def get_last_message_id_and_index(self, subtitle_id):
        document = await self.subtitles_collection.find_one(
            {"_id": subtitle_id},
            {"last_edited_line": 1, "last_message_id": 1, "_id": 0},
        )
        index = document.get("last_edited_line") if document else None
        message_id = document.get("last_message_id") if document else None
        return index, message_id

    async def get_last_message_id_index_and_collab_status(self, subtitle_id):
        document = await self.subtitles_collection.find_one(
            {"_id": subtitle_id},
            {"last_edited_line": 1, "last_message_id": 1, "collab_status": 1, "_id": 0},
        )
        index = document.get("last_edited_line") if document else None
        message_id = document.get("last_message_id") if document else None
        collab_status = document.get("collab_status") if document else None
        return index, message_id, collab_status

    async def update_error_message_id(self, subtitle_id, message_id):
        result = await self.subtitles_collection.update_one(
            {"_id": subtitle_id}, {"$set": {"error_message_id": message_id}}
        )
        return result.modified_count > 0

    async def update_subtitle_array(self, subtitle_id, subtitles):
        result = await self.subtitles_collection.update_one(
            {"_id": subtitle_id}, {"$set": {"subtitles": subtitles}}
        )

        return result.modified_count > 0

    # CRUD operations for 'users' collection
    async def create_user(self, user_data):
        try:
            result = await self.users_collection.insert_one(user_data)
        except DuplicateKeyError:
            LOGGER(__name__).error(
                f"User with username {user_data['username']} already exists."
            )
            return None
        return result.inserted_id

    async def read_user(self, user_id):
        user = await self.users_collection.find_one({"_id": user_id})
        return user

    async def update_user(self, user_id, update_data):
        result = await self.users_collection.update_one(
            {"_id": user_id}, {"$set": update_data}
        )
        return result.modified_count

    async def delete_user(self, user_id):
        result = await self.users_collection.delete_one({"_id": user_id})
        return result.deleted_count

    async def remove_subtitle_from_user(self, user_id, subtitle_id):
        # print(user_id)
        result = await self.users_collection.update_one(
            {"_id": user_id}, {"$pull": {"subtitles": {"id": subtitle_id}}}
        )
        return result.modified_count > 0

    async def update_language_code(self, user_id, language_code):
        result = await self.users_collection.update_one(
            {"_id": user_id}, {"$set": {"language_code": language_code}}
        )
        return result.modified_count > 0

    async def get_language_code(self, user_id):
        document = await self.users_collection.find_one(
            {"_id": user_id}, {"language_code": 1, "_id": 0}
        )
        return document.get("language_code") if document else None


db = MongoDB()


async def check_mongo_uri(mongo_uri: str) -> None:
    try:
        mongo = motor.motor_asyncio.AsyncIOMotorClient(mongo_uri)
        await mongo.server_info()
    except ServerSelectionTimeoutError:
        LOGGER(__name__).error(
            "Error in establishing connection with MongoDb URI. Please enter a valid URI in the config section."
        )
        exit(1)
