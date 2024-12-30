from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from .utils import save_data, load_data, get_main_keyboard
import logging
import os
from dotenv import load_dotenv

# Laden der Umgebungsvariablen aus der .env Datei
load_dotenv()

OWNER_ID = os.getenv('OWNER_ID')  # Stellen Sie sicher, dass OWNER_ID korrekt geladen wird
logger = logging.getLogger(__name__)

reported_users = load_data()

WAITING_FOR_DELETION_INFO = range(1)

async def delete_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        user_id = update.effective_user.id
        if str(user_id) != OWNER_ID:
            await update.message.reply_text("Sie haben keine Berechtigung, diese Aktion auszuführen.")
            return

        command, user_id_to_delete = update.message.text.split()
        user_id_to_delete = user_id_to_delete.strip()

        user_deleted = False

        if user_id_to_delete in reported_users["scammers"]:
            del reported_users["scammers"][user_id_to_delete]
            user_deleted = True

        if user_id_to_delete in reported_users["trusted"]:
            del reported_users["trusted"][user_id_to_delete]
            user_deleted = True

        if user_deleted:
            save_data(reported_users)  # Speichern Sie die aktualisierten Daten
            await update.message.reply_text(f"Benutzer {user_id_to_delete} wurde erfolgreich aus den Listen gelöscht.")
            logger.info(f"Benutzer {user_id_to_delete} wurde erfolgreich gelöscht.")
        else:
            await update.message.reply_text("Benutzer-ID nicht in den Listen gefunden.")
            logger.info(f"Benutzer-ID {user_id_to_delete} nicht in den Listen gefunden.")
    except ValueError:
        await update.message.reply_text("Ungültiges Format. Bitte verwenden Sie /del <user_id>.")
        logger.error("Ungültiges Format für /del Befehl.")

async def receive_deletion_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id_to_delete = update.message.text.strip()
    user_deleted = False

    if user_id_to_delete in reported_users["scammers"]:
        del reported_users["scammers"][user_id_to_delete]
        user_deleted = True

    if user_id_to_delete in reported_users["trusted"]:
        del reported_users["trusted"][user_id_to_delete]
        user_deleted = True

    if user_deleted:
        save_data(reported_users)  # Speichern Sie die aktualisierten Daten
        await update.message.reply_text(f"Benutzer {user_id_to_delete} wurde erfolgreich aus den Listen gelöscht.",
                                        reply_markup=get_main_keyboard())
        logger.info(f"Benutzer {user_id_to_delete} wurde erfolgreich gelöscht.")
    else:
        await update.message.reply_text("Benutzer-ID nicht in den Listen gefunden.",
                                        reply_markup=get_main_keyboard())
        logger.info(f"Benutzer-ID {user_id_to_delete} nicht in den Listen gefunden.")
    
    return ConversationHandler.END
