import asyncio
from functools import wraps
from typing import Callable, Union

from pyrogram import Client
from pyrogram.types import CallbackQuery, Message

from subedit import loop
from subedit.helpers.functions import isAdmin


def admin_commands(func: Callable) -> Callable:
    """
    Restricts user's from using group admin commands.
    """

    @wraps(func)
    async def decorator(client: Client, message: Message):
        if await isAdmin(message):
            return await func(client, message)

    return decorator


def errors(func: Callable) -> Callable:
    """
    Try and catch error of any function.
    """

    @wraps(func)
    async def decorator(client, message, *args, **kwargs):
        try:
            return await func(client, message, *args, **kwargs)
        except Exception as error:
            await message.reply(f"{type(error).__name__}: {error}")

    return decorator
