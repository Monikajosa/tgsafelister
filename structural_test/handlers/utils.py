import logging
import json
from telegram import ReplyKeyboardMarkup, KeyboardButton

logger = logging.getLogger(__name__)

def load_data():
    try:
        with open('reported_users.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"scammers": {}, "trusted": {}}

def save_data(reported_users):
    with open('reported_users.json', 'w') as f:
        json.dump(reported_users, f, indent=4)

def get_main_keyboard():
    keyboard = [
        [KeyboardButton("Scammer melden"), KeyboardButton("Trust melden")],
        [KeyboardButton("User prüfen")],
        [KeyboardButton("Löschung beantragen")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def escape_markdown(text):
    """Escapes markdown special characters."""
    escape_chars = r"\_*[]()~`>#+-=|{}.!"
    return ''.join(f'\\{char}' if char in escape_chars else char for char in text)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    await update.message.reply_text("Ein unerwarteter Fehler ist aufgetreten. Bitte versuchen Sie es später erneut.")

async def handle_support_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat_id == int(SUPPORT_GROUP_ID):
        if update.message.reply_to_message:
            reply_to_message_id = update.message.reply_to_message.message_id
            if reply_to_message_id in support_message_mapping:
                original_user_id = support_message_mapping[reply_to_message_id]
                await context.bot.send_message(chat_id=original_user_id, text=update.message.text)

                if update.message.text.lower().strip() == "end":
                    del support_message_mapping[reply_to_message_id]
                    del deletion_requests[original_user_id]
                    await context.bot.send_message(chat_id=original_user_id, text="Dein Ticket wurde geschlossen, für weitere Vorgehen eine neue Anfrage stellen.")
            else:
                await context.bot.send_message(chat_id=update.message.chat_id, text="Keine zugeordnete Support-Anfrage gefunden.")
        else:
            await context.bot.send_message(chat_id=update.message.chat_id, text="Keine zugeordnete Support-Anfrage gefunden.")
    else:
        user_id = update.message.from_user.id
        if user_id in deletion_requests and deletion_requests[user_id]:
            sent_message = await context.bot.send_message(chat_id=SUPPORT_GROUP_ID, text=f"Support-Anfrage von {user_id}:\n\n{update.message.text}")
            support_message_mapping[sent_message.message_id] = user_id
