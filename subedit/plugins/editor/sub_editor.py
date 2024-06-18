import pysrt
from subedit.database.database import (
    getSubtitleLines,
    getSubtitleByIndex,
    updateSubtitleEdited,
    updateLastIndex,
)


async def subExplorer(subtitle_id, offset):
    # Get the subtitle
    subtitle = await getSubtitleLines(subtitle_id, offset)
    return subtitle


async def fetchLine(subtitle_id, index):
    # Get the subtitle
    subtitle = await getSubtitleByIndex(subtitle_id, index)
    return subtitle


async def updateEdit(sub_id, index, edited_text):
    await updateLastIndex(sub_id, index)
    await updateSubtitleEdited(sub_id, index, edited_text)
    updated_subtitle = await getSubtitleByIndex(sub_id, index)
    return updated_subtitle
