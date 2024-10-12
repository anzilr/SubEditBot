from pyrogram import filters
import re
from subedit.logging import LOGGER

def CallbackDataFilter(data):
    async def func(flt, _, query):
        return flt.data == query.data
    # "data" kwarg is accessed with "flt.data" above
    return filters.create(func, data=data)


def CallbackButtonDataFilter(data):
    async def func(flt, _, query):
        Data = query.data.split("|")[0]
        return flt.data == Data

    # "data" kwarg is accessed with "flt.data" above
    return filters.create(func, data=data)


def UserStateFilter(user_db):
    async def func(flt, _, message):
        user_id = message.from_user.id
        try:
            if user_db[user_id]["state"] == "edit_time":
                return True
        except KeyError:
            return False

    # "message" kwarg is accessed with "_" above
    return filters.create(func, "UserStateFilter")


def collab_filter(_, __, message):
    # Regular expression to match '/collab' followed by a number
    if message.text is not None:
        return bool(re.match(r"^/collab \d+$", message.text))
