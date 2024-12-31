import logging
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, CallbackContext, ConversationHandler, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv
import os
import json
from .utils import get_main_keyboard  # Sicherstellen, dass importiert wird

# Laden der Umgebungsvariablen aus der .env Datei
load_dotenv()

SUPPORT_GROUP_ID = os.getenv('SUPPORT_GROUP_ID')

# Laden der gemeldeten Benutzer aus der JSON-Datei
REPORTED_USERS_FILE = 'structural_test/reported_users.json'

def load_reported_users():
    try:
        with open(REPORTED_USERS_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {"scammers": {}, "trusted": {}, "deletion_requests": {}}

reported_users = load_reported_users()

logger = logging.getLogger(__name__)

# Zustände für den ConversationHandler
WAITING_FOR_DELETION_INFO = range(1)

# Initialisiere die Datenstrukturen
SUPPORT_MAPPING_FILE = 'support_message_mapping.json'
TICKET_COUNTER_FILE = 'ticket_counter.json'

# Funktion zum Laden der Support-Nachrichten-Zuordnung
def load_support_message_mapping():
    if os.path.exists(SUPPORT_MAPPING_FILE):
        try:
            with open(SUPPORT_MAPPING_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Fehler beim Laden der support_message_mapping.json: {e}")
            return {}
    return {}

# Funktion zum Speichern der Support-Nachrichten-Zuordnung
def save_support_message_mapping(mapping):
    try:
        with open(SUPPORT_MAPPING_FILE, 'w') as f:
            json.dump(mapping, f, indent=4)
    except Exception as e:
        logging.error(f"Fehler beim Speichern der support_message_mapping.json: {e}")

# Funktion zum Laden des Ticketzählers
def load_ticket_counter():
    if os.path.exists(TICKET_COUNTER_FILE):
        try:
            with open(TICKET_COUNTER_FILE, 'r') as f:
                return json.load(f).get('ticket_counter', 1)
        except Exception as e:
            logging.error(f"Fehler beim Laden der ticket_counter.json: {e}")
            return 1
    return 1

# Funktion zum Speichern des Ticketzählers
def save_ticket_counter(counter):
    try:
        with open(TICKET_COUNTER_FILE, 'w') as f:
            json.dump({'ticket_counter': counter}, f, indent=4)
    except Exception as e:
        logging.error(f"Fehler beim Speichern der ticket_counter.json: {e}")

# Laden der Support-Nachrichten-Zuordnung und des Ticketzählers beim Start
support_message_mapping = load_support_message_mapping()
ticket_counter = load_ticket_counter()

async def request_deletion(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Bitte geben Sie die ID und den Grund für die Löschung in folgendem Format ein:\n\nID: Grund",
        reply_markup=ReplyKeyboardRemove()
    )
    return WAITING_FOR_DELETION_INFO

async def receive_deletion_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global support_message_mapping  # Verwende die globale Zuordnung

    # Ticketzähler unmittelbar vor der Erstellung eines neuen Tickets laden
    ticket_counter = load_ticket_counter()

    user_id = update.effective_user.id
    reason = update.message.text

    # Prüfen, ob der Benutzer in der Trust- oder Scammer-Liste ist
    status = 'None'
    if str(user_id) in reported_users['trusted']:
        status = 'Trust'
    elif str(user_id) in reported_users['scammers']:
        status = 'Scammer'

    support_message = f"Löschanfrage erhalten [Ticket #{ticket_counter}]:\nUser ID: {user_id}\nStatus: {status}\nBegründung: {reason}"
    sent_message = await context.bot.send_message(chat_id=SUPPORT_GROUP_ID, text=support_message)
    support_message_mapping[ticket_counter] = {
        'user_id': user_id,
        'support_message_id': sent_message.message_id
    }
    
    # Speichern der Änderungen in der Datei
    save_support_message_mapping(support_message_mapping)

    # Inkrementiere und speichere den Ticketzähler
    ticket_counter += 1
    save_ticket_counter(ticket_counter)
    
    await update.message.reply_text(f"Ihr Löschantrag wurde als Ticket #{ticket_counter - 1} eingereicht.", reply_markup=get_main_keyboard())
    return ConversationHandler.END

async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global support_message_mapping  # Verwende die globale Zuordnung

    user_id = update.effective_user.id
    open_ticket_number = None
    for ticket_number, data in support_message_mapping.items():
        if data['user_id'] == user_id:
            open_ticket_number = ticket_number
            break

    if open_ticket_number is not None:
        support_message = f"Nachricht von Benutzer {user_id} [Ticket #{open_ticket_number}]:\n\n{update.message.text}"
        sent_message = await context.bot.send_message(chat_id=SUPPORT_GROUP_ID, text=support_message)
        support_message_mapping[open_ticket_number]['support_message_id'] = sent_message.message_id
        save_support_message_mapping(support_message_mapping)
    else:
        await context.bot.send_message(chat_id=update.message.chat_id, text="Support-Anfragen können nur über den Button 'Löschung beantragen' eingereicht werden.")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Löschantrag abgebrochen.", reply_markup=get_main_keyboard())
    return ConversationHandler.END

deletion_conv_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex('^(Löschung beantragen)$'), request_deletion)],
    states={
        WAITING_FOR_DELETION_INFO: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_deletion_info)],
    },
    fallbacks=[CommandHandler("cancel", cancel)]
)

user_message_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_message)

async def error_handler(update: Update, context: CallbackContext) -> None:
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    await update.message.reply_text("Ein unerwarteter Fehler ist aufgetreten. Bitte versuchen Sie es später erneut.")
