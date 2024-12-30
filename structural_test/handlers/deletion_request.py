import logging
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
from dotenv import load_dotenv
import os
from .utils import get_main_keyboard  # Sicherstellen, dass importiert wird

# Laden der Umgebungsvariablen aus der .env Datei
load_dotenv()

SUPPORT_GROUP_ID = os.getenv('SUPPORT_GROUP_ID')
logger = logging.getLogger(__name__)

# Zustände für den ConversationHandler
WAITING_FOR_DELETION_INFO = range(1)

# Initialisiere die Datenstrukturen
ticket_counter = 1  # Zähler für die Ticketnummern
support_message_mapping = {}

async def request_deletion(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Bitte geben Sie die ID und den Grund für die Löschung in folgendem Format ein:\n\nID: Grund",
        reply_markup=ReplyKeyboardRemove()
    )
    return WAITING_FOR_DELETION_INFO

async def receive_deletion_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global ticket_counter  # Verwende den globalen Ticketzähler

    user_id = update.effective_user.id
    support_message = f"Löschanfrage erhalten [Ticket #{ticket_counter}]:\n{update.message.text}"
    sent_message = await context.bot.send_message(chat_id=SUPPORT_GROUP_ID, text=support_message)
    support_message_mapping[ticket_counter] = {
        'user_id': user_id,
        'support_message_id': sent_message.message_id
    }
    await update.message.reply_text(f"Ihr Löschantrag wurde als Ticket #{ticket_counter} eingereicht.", reply_markup=get_main_keyboard())
    ticket_counter += 1  # Inkrementiere die Ticketnummer für die nächste Anfrage
    return ConversationHandler.END
