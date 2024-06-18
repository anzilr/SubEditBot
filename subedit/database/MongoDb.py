from pymongo.errors import ServerSelectionTimeoutError, DuplicateKeyError
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

    async def get_sub_id(self, user_id):
        document = await self.users_collection.find_one(
            {"_id": user_id},
            {
                "subtitles": 1,
                "_id": 0,
            },  # Projecting to only include the subtitles array
        )
        return document.get("subtitles") if document else None

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
        result = await self.users_collection.update_one(
            {"_id": user_id}, {"$pull": {"subtitles": {"id": subtitle_id}}}
        )
        return result.modified_count > 0


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
