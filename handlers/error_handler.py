import logging
from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import TimedOut

logger = logging.getLogger(__name__)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        logger.error(msg="Exception while handling an update:", exc_info=context.error)
        await update.message.reply_text("Ein unerwarteter Fehler ist aufgetreten. Bitte versuchen Sie es später erneut.")
    except TimedOut:
        logger.error("Request timed out. Retrying...")
        # Hier können Sie Logik hinzufügen, um die Anfrage erneut zu senden oder andere Maßnahmen zu ergreifen.
