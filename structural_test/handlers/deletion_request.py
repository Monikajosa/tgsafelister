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

# Initialisiere die Datenstruktur für Zuordnung der Nachrichten-IDs zu Benutzer-IDs
support_message_mapping = {}
deletion_requests = {}

async def request_deletion(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Bitte geben Sie die ID und den Grund für die Löschung in folgendem Format ein:\n\nID: Grund",
        reply_markup=ReplyKeyboardRemove()
    )
    return WAITING_FOR_DELETION_INFO

async def receive_deletion_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    deletion_requests[user_id] = True  # Markiere die Löschanfrage als aktiv
    support_message = f"Löschanfrage erhalten:\n{update.message.text}"
    sent_message = await context.bot.send_message(chat_id=SUPPORT_GROUP_ID, text=support_message)
    support_message_mapping[sent_message.message_id] = user_id

    await update.message.reply_text("Ihr Löschantrag wurde eingereicht.", reply_markup=get_main_keyboard())
    return ConversationHandler.END
