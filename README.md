# SubEditBot

Welcome to **SubEditBot**! This Telegram bot is your ultimate tool for subtitle editing. With a range of features designed to make subtitle editing a breeze, SubEditBot is here to save you time and effort.

## Features

- **Re-sync SRT Files:** Quickly fix out-of-sync subtitles with ease.
- **Add and Remove Lines:** Easily add new lines or remove unwanted ones from your subtitle files.
- **Merge and Split Lines:** Combine multiple lines into one or split long lines into shorter segments.
- **Adjust Time of Lines:** Fine-tune the timing of your subtitles to perfection.
- **Inbuilt Color Picker and Text Formatter:** Access a web app to pick colors and format your text for more dynamic subtitles.
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

4. Run the bot:

```
python3 -m subedit
```

## Web App Integration
SubEditBot includes a web app for advanced text formatting and color picking. Access it via the Formatter button in the bot interface. Source [here](https://github.com/anzilr/TextFormatter)

## Contributing
We welcome contributions! If you have suggestions for improvements or find any bugs, please open an issue or submit a pull request.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements
- Thanks to the developers of pyrogram and pysrt for their awesome libraries.
- Special thanks to all contributors and users for their support.