import asyncio
import signal
import sys
import time
from asyncio import get_event_loop, new_event_loop, set_event_loop
from convopyro import Conversation
from pyrogram import Client
from subedit import config
from subedit.database.MongoDb import check_mongo_uri, db
from subedit.logging import LOGGER

LOGGER(__name__).info("Starting subedit....")
BotStartTime = time.time()

if sys.version_info[0] < 3 or sys.version_info[1] < 7:
    LOGGER(__name__).critical(
        """
=============================================================
You MUST need to be on python 3.7 or above, shutting down the bot...
=============================================================
"""
    )
    sys.exit(1)

LOGGER(__name__).info("setting up event loop....")
try:
    loop = get_event_loop()
except RuntimeError:
    set_event_loop(new_event_loop())
    loop = asyncio.get_event_loop()

LOGGER(__name__).info(
    """
    
███████╗██╗   ██╗██████╗ ███████╗██████╗ ██╗████████╗ ██████╗ ██████╗ 
██╔════╝██║   ██║██╔══██╗██╔════╝██╔══██╗██║╚══██╔══╝██╔═══██╗██╔══██╗
███████╗██║   ██║██████╔╝█████╗  ██║  ██║██║   ██║   ██║   ██║██████╔╝
╚════██║██║   ██║██╔══██╗██╔══╝  ██║  ██║██║   ██║   ██║   ██║██╔══██╗
███████║╚██████╔╝██████╔╝███████╗██████╔╝██║   ██║   ╚██████╔╝██║  ██║
╚══════╝ ╚═════╝ ╚═════╝ ╚══════╝╚═════╝ ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝
                                                                    
"""
)
# https://patorjk.com/software/taag/#p=display&f=Graffiti&t=Type%20Something%20


LOGGER(__name__).info("initiating the client....")
LOGGER(__name__).info("checking MongoDb URI....")


# loop.run_until_complete(check_mongo_uri(config.MONGO_URI))


def handle_signal(sig, frame):
    LOGGER(__name__).info("Shutting down gracefully...")
    bot.stop()
    db.client.close()
    loop.stop()


signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGTERM, handle_signal)

# https://docs.pyrogram.org/topics/smart-plugins
plugins = dict(root="subedit/plugins")
bot = Client(
    "subedit",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN,
    plugins=plugins,
)
Conversation(bot)
