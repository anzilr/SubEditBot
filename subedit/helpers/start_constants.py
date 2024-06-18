from subedit.version import (
    __python_version__,
    __version__,
    __pyro_version__,
    __license__,
)

USER_TEXT = """
🗒️ Documentation for commands available to user's 

• /start: To Get this message

• /help: Alias command for start

• /alive: Check if bot is alive or not.

• /ping: Alias command for alive.

• /edit: Start an editing session.
"""

SUDO_TEXT = """
🗒️ Documentation for Sudo Users commands.

• /speedtest: Check the internet speed of bot server.

• /serverstats: Get the stats of server.

• /dbstats: Get the stats of database 

• /stats: Alias command for serverstats

• /log: To get the log file of the bot.
"""

DEV_TEXT = """
🗒️ Documentation for Developers Commands.

• /update: Update the bot to latest commit from repository. 

• /restart: Restart the bot.

• /shell: Run the terminal commands via bot.

• /py: Run the python commands via bot

• /broadcast: Broadcast the message to bot users and chats.
"""

ABOUT_CAPTION = f"""• Python version : {__python_version__}
• Bot version : {__version__}
• pyrogram  version : {__pyro_version__}
• License : {__license__}

**Github Repo**: https://github.com/sanjit-sinha/TelegramBot-Boilerplate"""


START_CAPTION = """
Hey there, subtitle wizards! 🎬✨

Meet SubEditBot, your new best buddy for all things subtitles! This bot is here to make your subtitle editing life as smooth as a freshly buttered popcorn bucket. 🍿😎

What can SubEditBot do? Well, let’s just say it’s got more tricks up its sleeve than a magician at a cinema!

Features:

• Re-sync SRT Files: Is your subtitle out of sync? No problem! SubEditBot can fix it faster than you can say "Lights, camera, action!" 🎥

• Add and Remove Lines: Got a new zinger to add or a boring line to cut? SubEditBot's got you covered! ✂️📜

• Merge and Split Lines: Want to combine two lines into one epic quote or split a long monologue? Easy peasy! 🔀🔧

• Adjust Time of Lines: Need to tweak the timing? SubEditBot can handle it down to the millisecond! ⏱️⚙️

• Inbuilt Color Picker and Text Formatter: Choose your colors and format your text with our snazzy web app. Just click the Formatter button and start jazzing up those subtitles! 🎨🖋️

• Cloud Database: All your hard work is safely stored in the cloud. No more worries about losing unsaved work. It’s like having your personal subtitle fortress! ☁️🏰

And that’s just the tip of the iceberg! SubEditBot can do a lot more than that soon, but that’s enough to get you started. why wait? Let SubEditBot take your subtitle editing to the next level! 🎬🌟

Enjoy your editing adventures with SubEditBot! 📽️😄"""

COMMAND_CAPTION = """**Here are the list of commands which you can use in bot.\n**"""
