# [SubEditBot](t.me/SubEditBot)

Welcome to **[SubEditBot](t.me/SubEditBot)**! This Telegram bot is your ultimate tool for subtitle editing. With a range of features designed to make subtitle editing a breeze, SubEditBot is here to save you time and effort.

## Features

- **Re-sync SRT Files:** Quickly fix out-of-sync subtitles with ease.
- **Add and Remove Lines:** Easily add new lines or remove unwanted ones from your subtitle files.
- **Merge and Split Lines:** Combine multiple lines into one or split long lines into shorter segments.
- **Adjust Time of Lines:** Fine-tune the timing of your subtitles to perfection.
- **Inbuilt [Color Picker and Text Formatter](https://github.com/anzilr/TextFormatter):** Access a web app to pick colors and format your text for more dynamic subtitles.
- **Inbuilt [WebPlayer](https://github.com/anzilr/WebPlayer):** Preview the edited subtitles on a WbPlayer.
- **Extract subtitles from video files:** Send video files to extract subtitle tracks.
- **Collaborate with others:** The collaborative editing feature in SubEditBot allows multiple users to work together on editing subtitles. Authorized collaborators can access and modify subtitles in real-time, while administrators or original owners of the subtitle can manage permissions, such as blacklisting or removing collaborators. This feature enhances teamwork, ensuring efficient collaboration by allowing users to contribute, edit, or review subtitle files collectively within the bot’s interface.
- **Cloud Database:** All your subtitle editing is stored securely in the cloud, ensuring no loss of unsaved work.

## Getting Started

### Prerequisites

- Python 3.7+
- MongoDB (Cloud instance recommended)
- pyrogram
- pysrt

### Installation

1. Clone the repository:

```sh
git clone https://github.com/anzilr/SubEditBot.git
cd SubEditBot
```

2. Install the required packages:

```
pip install -r requirements.txt
```

3. Set up your config.env file with your Telegram bot token and MongoDB credentials.

Create a `config.env` file and write the below credentials
```python
API_ID="Your telegram API ID"
API_HASH="Your telegram API HASH"

MONGO_URI="Your MongoDB URI"
BOT_TOKEN="Your telegram bot token"

#SUDO USERID IS OPTIONAL
OWNER_USERID =[12345678]
SUDO_USERID  =[12345678]
DB_NAME = "Your MongoDB database name"
```

4. Run the bot:

```
python3 -m subedit
```

## File Structure
```python
SubEditBot/
├── 📄 .gitignore
├── 📄 config.env
├── 📁 downloads
├── 📄 LICENSE
├── 📄 README.md
├── 📄 requirements.txt
└── 📁 subedit
    ├── 🐍 config.py
    ├── 📁 database
    │   ├── 🐍 database.py
    │   ├── 🐍 MongoDb.py
    │   └── 🐍 __init__.py
    ├── 📁 helpers
    │   ├── 📁 assets
    │   │   ├── 📄 index.html
    │   │   ├── 🖼️ profile_picture.jpeg
    │   │   ├── 📄 script.js
    │   │   └── 📄 styles.css
    │   ├── 🐍 decorators.py
    │   ├── 📁 Filters
    │   │   ├── 🐍 custom_filters.py
    │   │   └── 🐍 __init__.py
    │   ├── 🐍 filters.py
    │   ├── 🐍 functions.py
    │   ├── 🐍 srt_parser.py
    │   ├── 🐍 start_constants.py
    │   └── 🐍 __init__.py
    ├── 🐍 logging.py
    ├── 📁 plugins
    │   ├── 📁 developer
    │   │   ├── 🐍 broadcast.py
    │   │   ├── 🐍 terminal.py
    │   │   ├── 🐍 updater.py
    │   │   └── 🐍 __init__.py
    │   ├── 📁 editor
    │   │   ├── 🐍 add_line.py
    │   │   ├── 🐍 adjust_time.py
    │   │   ├── 🐍 compile_subtitle.py
    │   │   ├── 🐍 delete_line.py
    │   │   ├── 🐍 delete_subtitle.py
    │   │   ├── 🐍 edit_inline_result_line.py
    │   │   ├── 🐍 edit_subtitle_line.py
    │   │   ├── 🐍 edit_text.py
    │   │   ├── 🐍 line_pagination.py
    │   │   ├── 🐍 merge_line.py
    │   │   ├── 🐍 resync_subtitles.py
    │   │   ├── 🐍 split_line.py
    │   │   ├── 🐍 sub_editor.py
    │   │   └── 🐍 __init__.py
    │   ├── 📁 handlers
    │   │   ├── 🐍 callbackQuery_handler.py
    │   │   ├── 🐍 inlineQuery_handler.py
    │   │   ├── 🐍 message_handler.py
    │   │   └── 🐍 __init__.py
    │   ├── 📁 sudo
    │   │   ├── 🐍 dbstats.py
    │   │   ├── 🐍 log.py
    │   │   └── 🐍 __init__.py
    │   ├── 📁 users
    │   │   ├── 🐍 ping.py
    │   │   ├── 🐍 start.py
    │   │   └── 🐍 __init__.py
    │   └── 🐍 __init__.py
    ├── 🐍 version.py
    ├── 🐍 __init__.py
    └── 🐍 __main__.py
```
## Web App Integration
SubEditBot includes a web app for advanced text formatting and color picking. Access it via the Formatter button in the bot interface. Source [here](https://github.com/anzilr/TextFormatter)

## WebPlayer
SubEditBot includes a [WebPlayer](https://github.com/anzilr/WebPlayer) for previewing the edited subtitles with video. Access it via the Player button in the bot interface.

## Contributing
We welcome contributions! If you have suggestions for improvements or find any bugs, please open an issue or submit a pull request.

## License
This project is licensed under the MIT License - see the [LICENSE](https://github.com/anzilr/SubEditBot/blob/master/LICENSE) file for details.

## Acknowledgements
- Thanks to the developers of pyrogram and pysrt for their awesome libraries.
- Special thanks to all contributors and users for their support.