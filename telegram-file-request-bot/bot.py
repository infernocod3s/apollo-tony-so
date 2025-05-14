import os
import logging
from datetime import datetime
from typing import Dict, List
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Store requests in memory (in production, use a database)
requests: Dict[str, List[dict]] = {}  # chat_id -> list of requests

class FileRequest:
    def __init__(self, request_id: str, requester_id: int, requester_name: str, 
                 target_user_id: int, target_username: str, link_name: str, url: str):
        self.request_id = request_id
        self.requester_id = requester_id
        self.requester_name = requester_name
        self.target_user_id = target_user_id
        self.target_username = target_username
        self.link_name = link_name
        self.url = url
        self.completed = False
        self.created_at = datetime.now()
        self.completed_at = None

    def to_dict(self):
        return {
            'request_id': self.request_id,
            'requester_id': self.requester_id,
            'requester_name': self.requester_name,
            'target_user_id': self.target_user_id,
            'target_username': self.target_username,
            'link_name': self.link_name,
            'url': self.url,
            'completed': self.completed,
            'created_at': self.created_at,
            'completed_at': self.completed_at
        }

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    await update.message.reply_text(
        'Hi! I am a File Request Bot. Use /help to see available commands.'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    help_text = """
Available commands:
/request @username link_name url - Send a file request to a specific user
/queue - View current pending requests
/help - Show this help message
    """
    await update.message.reply_text(help_text)

async def request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /request command."""
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

    # Create request
    request_id = f"{update.effective_chat.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    new_request = FileRequest(
        request_id=request_id,
        requester_id=update.effective_user.id,
        requester_name=update.effective_user.full_name,
        target_user_id=0,  # Will be updated when user responds
        target_username=target_username,
        link_name=link_name,
        url=url
    )

    # Store request
    if str(update.effective_chat.id) not in requests:
        requests[str(update.effective_chat.id)] = []
    requests[str(update.effective_chat.id)].append(new_request.to_dict())

    # Notify target user
    await update.message.reply_text(
        f"{target_username} has been requested to upload a file for '{link_name}'.\n"
        f"URL: {url}\n"
        f"Please upload the file in response to this message."
    )

async def queue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show current pending requests."""
    if not update.effective_chat.type in ['group', 'supergroup']:
        await update.message.reply_text("This command can only be used in groups!")
        return

    chat_id = str(update.effective_chat.id)
    if chat_id not in requests or not requests[chat_id]:
        await update.message.reply_text("No pending requests!")
        return

    pending_requests = [r for r in requests[chat_id] if not r['completed']]
    if not pending_requests:
        await update.message.reply_text("No pending requests!")
        return

    message = "Current pending requests:\n\n"
    for req in pending_requests:
        message += f"Request: {req['link_name']}\n"
        message += f"From: {req['requester_name']}\n"
        message += f"To: {req['target_username']}\n"
        message += f"URL: {req['url']}\n"
        message += "-------------------\n"

    await update.message.reply_text(message)

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle file uploads and mark requests as complete."""
    if not update.effective_chat.type in ['group', 'supergroup']:
        return

    chat_id = str(update.effective_chat.id)
    if chat_id not in requests:
        return

    # Find the most recent incomplete request for this user
    user_requests = [r for r in requests[chat_id] 
                    if not r['completed'] and r['target_username'] == f"@{update.effective_user.username}"]
    
    if not user_requests:
        return

    # Mark the request as complete
    request = user_requests[0]
    request['completed'] = True
    request['completed_at'] = datetime.now()
    request['target_user_id'] = update.effective_user.id

    # Notify the group
    await update.message.reply_text(
        f"✅ Request '{request['link_name']}' has been completed by {update.effective_user.full_name}!"
    )

def main():
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(os.getenv('BOT_TOKEN')).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("request", request))
    application.add_handler(CommandHandler("queue", queue))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_file))

    # Start the Bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main() 