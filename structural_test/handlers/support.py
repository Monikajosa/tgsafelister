import logging
from telegram import Update
from telegram.ext import ContextTypes
from config import SUPPORT_GROUP_ID

# Initialisiere die Datenstrukturen
ticket_counter = 1  # Zähler für die Ticketnummern
support_message_mapping = {}  # Zuordnung von Ticketnummer zu Benutzer-ID

async def handle_support_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat_id == int(SUPPORT_GROUP_ID):
        # Nachrichten in der Support-Gruppe verarbeiten
        if update.message.reply_to_message:
            reply_to_message_id = update.message.reply_to_message.message_id
            for ticket_number, data in support_message_mapping.items():
                if data['support_message_id'] == reply_to_message_id:
                    original_user_id = data['user_id']
                    await context.bot.send_message(chat_id=original_user_id, text=f"[Ticket #{ticket_number}]\n{update.message.text}")

                    # Entfernen der Zuordnung nach Abschluss der Kommunikation
                    if update.message.text.lower().strip() == "end":
                        del support_message_mapping[ticket_number]
                        await context.bot.send_message(chat_id=original_user_id, text=f"Dein Ticket #{ticket_number} wurde geschlossen. Für weitere Anliegen bitte eine neue Anfrage stellen.")
                    break
            else:
                await context.bot.send_message(chat_id=update.message.chat_id, text="Keine zugeordnete Support-Anfrage gefunden.")
        else:
            await context.bot.send_message(chat_id=update.message.chat_id, text="Keine zugeordnete Support-Anfrage gefunden.")
    else:
        # Nachrichten von Benutzern außerhalb der Support-Gruppe verarbeiten
        global ticket_counter  # Verwende den globalen Ticketzähler
        user_id = update.message.from_user.id
        sent_message = await context.bot.send_message(chat_id=SUPPORT_GROUP_ID, text=f"Support-Anfrage von {user_id} [Ticket #{ticket_counter}]:\n\n{update.message.text}")
        support_message_mapping[ticket_counter] = {
            'user_id': user_id,
            'support_message_id': sent_message.message_id
        }
        await update.message.reply_text(f"Deine Support-Anfrage wurde als Ticket #{ticket_counter} eingereicht.")
        ticket_counter += 1  # Inkrementiere die Ticketnummer für die nächste Anfrage
