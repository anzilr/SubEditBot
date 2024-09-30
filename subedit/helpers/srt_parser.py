import pysrt
from subedit.database.database import createSubtitleDocument, updateSubtitleID
from subedit.logging import LOGGER
import traceback


async def srtParser(user_id, file_path, subtitle_id, file_name):
    try:
        subs = pysrt.open(file_path)
        subtitle_data = []
        for sub in subs:
            subtitle_entry = {
                "index": sub.index,
                "start_time": str(sub.start),
                "end_time": str(sub.end),
                "original": sub.text,
                "edited": None,
            }
            subtitle_data.append(subtitle_entry)
        sub_document = {
            "_id": subtitle_id,
            "file_name": file_name,
            "project_name": "Editor123",
            "last_edited_line": None,
            "last_message_id": None,
            "error_message_id": None,
            "collab_admin": user_id,
            "subtitles": subtitle_data,
        }
        sub_data = {"id": subtitle_id, "file_name": file_name}
        await createSubtitleDocument(sub_document)
        await updateSubtitleID(user_id, sub_data)
        LOGGER(__name__).info("Uploaded subtitle objects")
        return True
    except Exception as e:
        LOGGER(__name__).exception(traceback.format_exception(e))
        return False
