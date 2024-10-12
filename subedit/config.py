import json
from os import getenv
from dotenv import load_dotenv

load_dotenv("config.env")

API_ID = int(getenv("API_ID"))
API_HASH = getenv("API_HASH")
BOT_TOKEN = getenv("BOT_TOKEN")

OWNER_USERID = json.loads(getenv("OWNER_USERID"))
SUDO_USERID = OWNER_USERID
try:
    SUDO_USERID += json.loads(getenv("SUDO_USERID"))
except:
    pass
SUDO_USERID = list(set(SUDO_USERID))

MONGO_URI = getenv("MONGO_URI")
DB_NAME = getenv("DB_NAME")
MAIL_API = getenv("MAIL_API")
