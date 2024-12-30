from telegram import Update
from telegram.ext import ContextTypes
from .utils import save_data, load_data

reported_users = load_data()

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
            save_data()
            await update.message.reply_text(f"Benutzer {user_id_to_delete} wurde erfolgreich aus den Listen gelöscht.")
            logger.info(f"Benutzer {user_id_to_delete} wurde erfolgreich gelöscht.")
        else:
            await update.message.reply_text("Benutzer-ID nicht in den Listen gefunden.")
            logger.info(f"Benutzer-ID {user_id_to_delete} nicht in den Listen gefunden.")
    except ValueError:
        await update.message.reply_text("Ungültiges Format. Bitte verwenden Sie /del <user_id>.")
        logger.error("Ungültiges Format für /del Befehl.")
