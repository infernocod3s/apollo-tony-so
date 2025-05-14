import os
import logging
import datetime
import asyncio
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Store requests in memory
requests = {}

# Bot token
BOT_TOKEN = "8158879689:AAH2laSWl-k1KX0MMzLptBJlCeNzknOHvNk"

# Flask app for keep-alive
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

class FileRequest:
    def __init__(self, request_id, requester_id, target_user_id, link_name, url):
        self.request_id = request_id
        self.requester_id = requester_id
        self.target_user_id = target_user_id
        self.link_name = link_name
        self.url = url
        self.created_at = datetime.datetime.now()
        self.completed = False
        self.completed_at = None

    def to_dict(self):
        return {
            'request_id': self.request_id,
            'requester_id': self.requester_id,
            'target_user_id': self.target_user_id,
            'link_name': self.link_name,
            'url': self.url,
            'created_at': self.created_at,
            'completed': self.completed,
            'completed_at': self.completed_at
        }

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to the File Request Bot!\n\n"
        "I help manage file requests in groups. Here's how to use me:\n\n"
        "1. To request a file from someone:\n"
        "   /request @username link_name url\n\n"
        "2. To view pending requests:\n"
        "   /queue\n\n"
        "3. To get help:\n"
        "   /help"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 Available commands:\n\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/request @username link_name url - Request a file from a user\n"
        "/queue - Show pending requests in this group"
    )

async def request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat.type in ['group', 'supergroup']:
        await update.message.reply_text("This command can only be used in groups!")
        return

    if len(context.args) < 3:
        await update.message.reply_text(
            "Please use the format: /request @username link_name url"
        )
        return

    target_username = context.args[0]
    if not target_username.startswith('@'):
        await update.message.reply_text("Please mention the user with @")
        return

    link_name = context.args[1]
    url = context.args[2]

    # Generate a unique request ID
    request_id = f"{update.effective_chat.id}_{len(requests) + 1}"

    # Create new request
    new_request = FileRequest(
        request_id=request_id,
        requester_id=update.effective_user.id,
        target_user_id=target_username,
        link_name=link_name,
        url=url
    )

    # Store request
    if update.effective_chat.id not in requests:
        requests[update.effective_chat.id] = []
    requests[update.effective_chat.id].append(new_request)

    # Notify the group
    await update.message.reply_text(
        f"📝 New file request:\n"
        f"From: {update.effective_user.mention_html()}\n"
        f"To: {target_username}\n"
        f"Link: {link_name}\n"
        f"URL: {url}"
    )

async def queue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat.type in ['group', 'supergroup']:
        await update.message.reply_text("This command can only be used in groups!")
        return

    chat_id = update.effective_chat.id
    if chat_id not in requests or not requests[chat_id]:
        await update.message.reply_text("No pending requests in this group!")
        return

    message = "📋 Pending Requests:\n\n"
    for req in requests[chat_id]:
        if not req.completed:
            message += (
                f"Request ID: {req.request_id}\n"
                f"From: {req.requester_id}\n"
                f"To: {req.target_user_id}\n"
                f"Link: {req.link_name}\n"
                f"URL: {req.url}\n"
                f"Created: {req.created_at}\n\n"
            )

    await update.message.reply_text(message)

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat.type in ['group', 'supergroup']:
        return

    chat_id = update.effective_chat.id
    if chat_id not in requests:
        return

    user_id = update.effective_user.id
    for req in requests[chat_id]:
        if not req.completed and str(req.target_user_id) == f"@{update.effective_user.username}":
            req.completed = True
            req.completed_at = datetime.datetime.now()
            await update.message.reply_text(
                f"✅ Request {req.request_id} has been completed!\n"
                f"File uploaded by {update.effective_user.mention_html()}"
            )

def main():
    # Start the keep-alive server
    keep_alive()
    
    # Initialize bot
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("request", request))
    application.add_handler(CommandHandler("queue", queue))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_file))

    # Start the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main() 