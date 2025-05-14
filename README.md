# Telegram File Request Bot

A Telegram bot that manages file requests in group chats. Users can send link requests to specific users, who can then respond by uploading files.

## Features

- Send link requests to specific users in a group
- Name your requests for better organization
- Queue system for tracking current requests
- Automatic completion marking when files are uploaded
- Group-based interaction

## Setup

1. Create a new bot using [@BotFather](https://t.me/botfather) on Telegram
2. Get your bot token and add it to `.env` file:
   ```
   BOT_TOKEN=your_bot_token_here
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Run the bot:
   ```
   python bot.py
   ```

## Usage

1. Add the bot to your group
2. Use the following commands:
   - `/request @username link_name url` - Send a file request to a specific user
   - `/queue` - View current pending requests
   - `/help` - Show available commands

## Note

Make sure the bot has admin privileges in the group to function properly. 