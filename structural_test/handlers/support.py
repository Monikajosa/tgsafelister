import logging
from telegram import Update
from telegram.ext import ContextTypes
from config import SUPPORT_GROUP_ID

# Initialisiere die Datenstruktur für Zuordnung der Nachrichten-IDs zu Benutzer-IDs
support_message_mapping = {}
deletion_requests = {}

async def handle_support_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat_id == int(SUPPORT_GROUP_ID):
        # Nachrichten in der Support-Gruppe verarbeiten
        if update.message.reply_to_message:
            reply_to_message_id = update.message.reply_to_message.message_id
            if reply_to_message_id in support_message_mapping:
                original_user_id = support_message_mapping[reply_to_message_id]
                await context.bot.send_message(chat_id=original_user_id, text=update.message.text)

                # Entfernen der Zuordnung nach Abschluss der Kommunikation
                if update.message.text.lower().strip() == "end":
                    del support_message_mapping[reply_to_message_id]
                    del deletion_requests[original_user_id]  # Beende die Löschanfrage
                    await context.bot.send_message(chat_id=original_user_id, text="Dein Ticket wurde geschlossen, für weitere Vorgehen eine neue Anfrage stellen.")
            else:
                await context.bot.send_message(chat_id=update.message.chat_id, text="Keine zugeordnete Support-Anfrage gefunden.")
        else:
            await context.bot.send_message(chat_id=update.message.chat_id, text="Keine zugeordnete Support-Anfrage gefunden.")
    else:
        # Nachrichten von Benutzern außerhalb der Support-Gruppe verarbeiten
        user_id = update.message.from_user.id
        if user_id in deletion_requests and deletion_requests[user_id]:
            sent_message = await context.bot.send_message(chat_id=SUPPORT_GROUP_ID, text=f"Support-Anfrage von {user_id}:\n\n{update.message.text}")
            support_message_mapping[sent_message.message_id] = user_id
