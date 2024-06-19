from subedit import bot
from subedit.plugins.editor.sub_editor import subExplorer
from pyrogram.types import (
    InlineQueryResultArticle,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InputTextMessageContent,
)


@bot.on_inline_query()
async def exploreInline(client, inline_query):
    sub_id = inline_query.query
    if inline_query.offset:
        offset = int(inline_query.offset)
    else:
        offset = 0
    if sub_id is None:
        return
    results = await subExplorer(sub_id, offset)
    next_offset = offset + 50
    inline_results = []
    for result in results:
        index = result["index"]
        start_time = result["start_time"]
        end_time = result["end_time"]
        timecode = f"{start_time} --> {end_time}"
        subtitle = result["original"]
        edited_subtitle = result["edited"]
        if edited_subtitle is None:
            content = f"{index}\n{timecode}\n{subtitle}"
        else:
            content = f"{index}\n{timecode}\n<i>Original</i>\n{subtitle}\n\n<i>Edited</i>\n{edited_subtitle}"
        inline_results.append(
            InlineQueryResultArticle(
                title=f"{index}\n{timecode}",
                description=subtitle,
                input_message_content=InputTextMessageContent(message_text=content),
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="📝 Edit Line",
                                callback_data=f"EDIT_LINE|{sub_id}|{index}",
                            ),
                            InlineKeyboardButton(
                                text="🗑️ Delete Line",
                                callback_data=f"DELETE_LINE|{sub_id}|{index}",
                            ),
                        ]
                    ]
                ),
            )
        )
    await inline_query.answer(results=inline_results, next_offset=str(next_offset))
