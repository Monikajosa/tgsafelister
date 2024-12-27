import logging
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, KeyboardButtonRequestUser, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes
import json
from datetime import datetime
import os
from dotenv import load_dotenv

# Laden der Umgebungsvariablen aus .env
load_dotenv()

# Logging konfigurieren
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot-Token aus der Umgebungsvariablen
TOKEN = os.getenv('TELEGRAM_TOKEN')
SUPPORT_GROUP_ID = os.getenv('SUPPORT_GROUP_ID')  # ID der Support-Gruppe

# Datenstruktur für gemeldete Benutzer
reported_users = {
    "scammers": {},
    "trusted": {}
}

# Zustände für den ConversationHandler
SELECTING_USER, WAITING_FOR_FULL_NAME, WAITING_FOR_USERNAME, WAITING_FOR_REASON, UPDATING_USER, WAITING_FOR_DELETION_INFO, CHECKING_LIST = range(
    7)


def load_data():
    try:
        with open('reported_users.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"scammers": {}, "trusted": {}}


def save_data():
    with open('reported_users.json', 'w') as f:
        json.dump(reported_users, f)


# Laden Sie die Daten beim Start des Bots
reported_users = load_data()

# Datenstruktur für Zuordnung der Nachrichten-IDs zu Benutzer-IDs
support_message_mapping = {}


def get_main_keyboard():
    keyboard = [
        [KeyboardButton("Scammer melden"), KeyboardButton("Trust melden")],
        [KeyboardButton("User prüfen")],
        [KeyboardButton("Löschung beantragen")]  # Hinzufügen des Löschantrag-Buttons
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        '👋 Willkommen beim Telegram Sicherheits-Bot! \n\n'
        'Dieser Bot hilft Ihnen, sich vor Betrügern auf Telegram zu schützen. 🚫🔒 \n'
        'Bitte beachten Sie, dass der Bot keine Garantie für die Sicherheit Ihrer Daten geben kann. \n\n'
        'Wählen Sie eine der folgenden Optionen:',
        reply_markup=get_main_keyboard()
    )


# Der Rest des Codes bleibt unverändert...
async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    if text == "Scammer melden":
        return await start_report(update, context, "scammers")
    elif text == "Trust melden":
        return await start_report(update, context, "trusted")
    elif text == "User prüfen":
        return await start_check(update, context)
    elif text == "Löschung beantragen":
        await update.message.reply_text(
            "Bitte geben Sie die ID und den Grund für die Löschung in folgendem Format ein:\n\nID: Grund")
        return WAITING_FOR_DELETION_INFO


async def start_report(update: Update, context: ContextTypes.DEFAULT_TYPE, report_type: str) -> int:
    context.user_data['report_type'] = report_type
    button = KeyboardButton(
        text="Nutzer auswählen",
        request_user=KeyboardButtonRequestUser(
            request_id=1,
            user_is_bot=False,
            user_is_premium=None
        )
    )
    reply_markup = ReplyKeyboardMarkup([[button]], one_time_keyboard=True)
    await update.message.reply_text(
        f"Bitte wählen Sie den Nutzer aus, den Sie als {report_type[:-1]} melden möchten:",
        reply_markup=reply_markup
    )
    return SELECTING_USER


async def start_check(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    button = KeyboardButton(
        text="Nutzer auswählen",
        request_user=KeyboardButtonRequestUser(
            request_id=1,
            user_is_bot=False,
            user_is_premium=None
        )
    )
    reply_markup = ReplyKeyboardMarkup([[button]], one_time_keyboard=True)
    await update.message.reply_text(
        "Bitte wählen Sie den Nutzer aus, den Sie prüfen möchten:",
        reply_markup=reply_markup
    )
    return CHECKING_LIST


async def user_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_shared = update.message.user_shared
    if user_shared:
        selected_user_id = user_shared.user_id
        context.user_data['reported_user_id'] = selected_user_id
        report_type = context.user_data['report_type']

        # Überprüfen ob der Nutzer bereits gemeldet wurde
        if str(selected_user_id) in reported_users[report_type]:
            existing_data = reported_users[report_type][str(selected_user_id)]
            message = (
                f"Dieser Benutzer wurde bereits gemeldet:\n"
                f"**ID:** {escape_markdown(str(selected_user_id))}\n"
                f"**Vollständiger Name:** {escape_markdown(existing_data.get('full_name', 'Unbekannt'))}\n"
                f"**Benutzername:** {escape_markdown(existing_data.get('username', 'Nicht vorhanden'))}\n"
                f"**Grund:** {escape_markdown(existing_data['reason'])}\n"
                f"**Gemeldet am:** {escape_markdown(existing_data.get('first_reported_at', 'Unbekannt').split('T')[0])}\n"
                f"**Zuletzt gemeldet am:** {escape_markdown(existing_data.get('last_reported_at', 'Unbekannt').split('T')[0])}\n"
                f"**Meldungen insgesamt:** {existing_data['count']}\n\n"
                f"Möchten Sie die Informationen aktualisieren oder den Nutzer erneut melden?"
            )
            await update.message.reply_text(message, parse_mode='MarkdownV2')
            # Optionen zur Aktualisierung oder erneuten Meldung anbieten
            keyboard = [
                [KeyboardButton("Daten aktualisieren")],
                [KeyboardButton("Erneut melden")]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard)
            await update.message.reply_text("Wählen Sie eine Option:", reply_markup=reply_markup)
            return UPDATING_USER  # Zustand für die Entscheidung des Nutzers

        # Fragen Sie nach dem vollständigen Namen
        await update.message.reply_text("Bitte geben Sie den vollständigen Namen des ausgewählten Nutzers ein:",
                                        reply_markup=ReplyKeyboardRemove())
        return WAITING_FOR_FULL_NAME  # Zustand für die Eingabe des vollständigen Namens
    else:
        await update.message.reply_text("Kein Benutzer ausgewählt. Bitte versuchen Sie es erneut.",
                                        reply_markup=get_main_keyboard())
        return ConversationHandler.END


async def check_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_shared = update.message.user_shared
    if user_shared:
        selected_user_id = user_shared.user_id

        # Überprüfen ob der Nutzer in einer der Listen ist
        if str(selected_user_id) in reported_users["scammers"]:
            user_data = reported_users["scammers"][str(selected_user_id)]
            message = (
                f"❗😡__**Scamerliste**__😡❗\n"
                f"❗😡__**hier solltest du vorsichtig sein**__😡❗\n\n"
                f"**ID:** {escape_markdown(str(selected_user_id))}\n"
                f"**Vollständiger Name:** {escape_markdown(user_data.get('full_name', 'Unbekannt'))}\n"
                f"**Benutzername:** {escape_markdown(user_data.get('username', 'Nicht vorhanden'))}\n"
                f"**Grund:** {escape_markdown(user_data['reason'])}\n"
                f"**Gemeldet am:** {escape_markdown(user_data.get('first_reported_at', 'Unbekannt').split('T')[0])}\n"
                f"**Zuletzt gemeldet am:** {escape_markdown(user_data.get('last_reported_at', 'Unbekannt').split('T')[0])}\n"
                f"**Meldungen insgesamt:** {user_data['count']}\n"
            )
            await update.message.reply_text(message, parse_mode='MarkdownV2', reply_markup=get_main_keyboard())
        elif str(selected_user_id) in reported_users["trusted"]:
            user_data = reported_users["trusted"][str(selected_user_id)]
            message = (
                f"💚🦺__**Trustliste**__🦺💚\n"
                f"💚🦺__**diesem User kann man trauen**__🦺💚\n\n"
                f"**ID:** {escape_markdown(str(selected_user_id))}\n"
                f"**Vollständiger Name:** {escape_markdown(user_data.get('full_name', 'Unbekannt'))}\n"
                f"**Benutzername:** {escape_markdown(user_data.get('username', 'Nicht vorhanden'))}\n"
                f"**Grund:** {escape_markdown(user_data['reason'])}\n"
                f"**Gemeldet am:** {escape_markdown(user_data.get('first_reported_at', 'Unbekannt').split('T')[0])}\n"
                f"**Zuletzt gemeldet am:** {escape_markdown(user_data.get('last_reported_at', 'Unbekannt').split('T')[0])}\n"
                f"**Meldungen insgesamt:** {user_data['count']}\n"
            )
            await update.message.reply_text(message, parse_mode='MarkdownV2', reply_markup=get_main_keyboard())
        else:
            await update.message.reply_text("Dieser Nutzer ist nicht in der Scammerliste oder Trustliste.",
                                            reply_markup=get_main_keyboard())
        return ConversationHandler.END
    else:
        await update.message.reply_text("Kein Benutzer ausgewählt. Bitte versuchen Sie es erneut.",
                                        reply_markup=get_main_keyboard())
        return ConversationHandler.END


async def handle_update_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    choice = update.message.text
    if choice == "Daten aktualisieren":
        # Fragen Sie erneut nach vollständigem Namen
        await update.message.reply_text("Bitte geben Sie den vollständigen Namen des ausgewählten Nutzers ein:",
                                        reply_markup=ReplyKeyboardRemove())
        return WAITING_FOR_FULL_NAME
    elif choice == "Erneut melden":
        # Fragen Sie erneut nach dem Meldegrund
        await update.message.reply_text("Bitte geben Sie den Meldegrund an:", reply_markup=ReplyKeyboardRemove())
        return WAITING_FOR_REASON
    else:
        await update.message.reply_text("Ungültige Auswahl. Bitte versuchen Sie es erneut.",
                                        reply_markup=get_main_keyboard())
        return ConversationHandler.END


async def receive_full_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    full_name = update.message.text or "Kein vollständiger Name angegeben"  # Standardwert bei leerer Eingabe
    reported_user_id = context.user_data['reported_user_id']
    report_type = context.user_data['report_type']

    # Speichern des vollständigen Namens in der Datenstruktur und Initialisierung des Zählers
    current_time = datetime.now().isoformat()
    reported_users[report_type][str(reported_user_id)] = {
        "link": f"tg://user?id={reported_user_id}",
        "full_name": full_name,
        "username": "",
        "reason": "",
        "reported_by": update.effective_user.id,
        "first_reported_at": current_time,
        "last_reported_at": current_time,
        "count": 1  # Zähler für Meldungen initialisieren
    }

    # Fragen Sie nach dem Benutzernamen oder bieten Sie die Option an.
    keyboard = [
        [KeyboardButton("Überspringen")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Bitte geben Sie den Benutzernamen des ausgewählten Nutzers ein (oder wählen Sie 'Überspringen'):",
        reply_markup=reply_markup)

    return WAITING_FOR_USERNAME  # Zustand für die Eingabe des Benutzernamens


async def receive_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text == "Überspringen":
        username = "Nicht vorhanden"  # Setzen Sie den Benutzernamen auf "Nicht vorhanden"
    else:
        username = update.message.text or "Nicht vorhanden"  # Benutzername kann leer sein

    reported_user_id = context.user_data['reported_user_id']
    report_type = context.user_data['report_type']

    # Aktualisieren des Benutzernamens in der Datenstruktur
    reported_users[report_type][str(reported_user_id)]["username"] = username

    await update.message.reply_text("Bitte geben Sie nun den Meldegrund an:", reply_markup=ReplyKeyboardRemove())

    return WAITING_FOR_REASON  # Zum nächsten Zustand wechseln


async def receive_reason(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reason = update.message.text
    reported_user_id = context.user_data['reported_user_id']
    report_type = context.user_data['report_type']

    # Aktualisieren des Grundes in der Datenstruktur und Zähler erhöhen
    if str(reported_user_id) in reported_users[report_type]:
        reported_users[report_type][str(reported_user_id)]["reason"] = reason
        reported_users[report_type][str(reported_user_id)]["last_reported_at"] = datetime.now().isoformat()
        reported_users[report_type][str(reported_user_id)]["count"] += 1  # Zähler erhöhen

    await update.message.reply_text(f"Benutzer wurde erfolgreich als {report_type[:-1]} gemeldet.",
                                    reply_markup=get_main_keyboard())

    save_data()

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Meldung abgebrochen.", reply_markup=get_main_keyboard())

    return ConversationHandler.END


def escape_markdown(text):
    """Escapes markdown special characters."""
    escape_chars = r"\_*[]()~`>#+-=|{}.!"
    return ''.join(f'\\{char}' if char in escape_chars else char for char in text)


async def check_user_status(context: ContextTypes.DEFAULT_TYPE):
    for list_type in ["scammers", "trusted"]:
        for user_id in list(reported_users[list_type].keys()):
            try:
                await context.bot.get_chat(int(user_id))
            except Exception as e:
                logger.error(f"Fehler beim Überprüfen des Benutzers {user_id}: {e}")
                reported_users[list_type][user_id]['account_status'] = 'Nicht verfügbar oder gelöscht'

    save_data()


async def receive_deletion_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Weiterleiten der Nachricht an die Support-Gruppe
    support_message = f"Löschanfrage erhalten:\n{update.message.text}"
    sent_message = await context.bot.send_message(chat_id=SUPPORT_GROUP_ID, text=support_message)
    support_message_mapping[sent_message.message_id] = update.effective_user.id  # Zuordnung speichern

    await update.message.reply_text("Ihr Löschantrag wurde eingereicht.", reply_markup=get_main_keyboard())
    return ConversationHandler.END


async def handle_support_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat_id == int(SUPPORT_GROUP_ID):
        # Nachricht stammt aus der Support-Gruppe
        logger.info(f"Received message in support group: {update.message.message_id}")
        if update.message.reply_to_message:
            reply_to_message_id = update.message.reply_to_message.message_id
            logger.info(f"Reply to message ID: {reply_to_message_id}")
            if reply_to_message_id in support_message_mapping:
                original_user_id = support_message_mapping[reply_to_message_id]
                logger.info(f"Found original user ID: {original_user_id}")
                await context.bot.send_message(chat_id=original_user_id, text=update.message.text)
            else:
                logger.info(f"No mapping found for reply_to_message_id: {reply_to_message_id}")
                await context.bot.send_message(chat_id=update.message.chat_id,
                                               text="Keine zugeordnete Support-Anfrage gefunden.")
        else:
            logger.info("No reply_to_message found in update.")
            await context.bot.send_message(chat_id=update.message.chat_id,
                                           text="Keine zugeordnete Support-Anfrage gefunden.")
    else:
        user_id = update.message.from_user.id
        sent_message = await context.bot.send_message(chat_id=SUPPORT_GROUP_ID,
                                                      text=f"Support-Anfrage von {user_id}:\n\n{update.message.text}")
        logger.info(f"Original message ID: {sent_message.message_id}, User ID: {user_id}")
        support_message_mapping[sent_message.message_id] = user_id


def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a Telegram message to notify the developer."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    # Notify the user
    update.message.reply_text("Ein unerwarteter Fehler ist aufgetreten. Bitte versuchen Sie es später erneut.")


def main() -> None:
    application = Application.builder().token(TOKEN).build()

    report_conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex('^(Scammer melden|Trust melden)$'), handle_main_menu)
        ],
        states={
            SELECTING_USER: [MessageHandler(filters.StatusUpdate.USER_SHARED, user_selected)],
            UPDATING_USER: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_update_choice)],
            WAITING_FOR_FULL_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_full_name)],
            WAITING_FOR_USERNAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND | filters.Regex('^Überspringen$'), receive_username)],
            WAITING_FOR_REASON: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_reason)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    check_list_conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex('^(User prüfen)$'), handle_main_menu)
        ],
        states={
            CHECKING_LIST: [MessageHandler(filters.StatusUpdate.USER_SHARED, check_user)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    deletion_conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex('^(Löschung beantragen)$'), handle_main_menu)
        ],
        states={
            WAITING_FOR_DELETION_INFO: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_deletion_info)]
        },
        fallbacks=[CommandHandler("cancel", lambda update, context: update.message.reply_text("Meldung abgebrochen.",
                                                                                              reply_markup=get_main_keyboard()))]
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(report_conv_handler)
    application.add_handler(check_list_conv_handler)
    application.add_handler(deletion_conv_handler)
    application.add_handler(MessageHandler(filters.ALL, handle_support_message))

    job_queue = application.job_queue
    job_queue.run_repeating(check_user_status, interval=86400)

    # Register the error handler
    application.add_error_handler(error_handler)

    application.run_polling()


if __name__ == '__main__':
    main()
