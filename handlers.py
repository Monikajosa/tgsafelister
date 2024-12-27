import logging
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButtonRequestUser
from telegram.ext import ContextTypes, ConversationHandler
import json
from datetime import datetime
from config import SUPPORT_GROUP_ID

# Logging konfigurieren
logger = logging.getLogger(__name__)

# Datenstruktur für gemeldete Benutzer
reported_users = {
    "scammers": {},
    "trusted": {}
}

# Zustände für den ConversationHandler
SELECTING_USER, WAITING_FOR_FULL_NAME, WAITING_FOR_USERNAME, WAITING_FOR_REASON, UPDATING_USER, WAITING_FOR_DELETION_INFO, CHECKING_LIST = range(7)

def load_data():
    try:
        with open('reported_users.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"scammers": {}, "trusted": {}}

def save_data():
    with open('reported_users.json', 'w') as f:
        json.dump(reported_users, f, indent=4)

# Laden der Daten beim Start des Bots
reported_users = load_data()

# Datenstruktur für Zuordnung der Nachrichten-IDs zu Benutzer-IDs
support_message_mapping = {}

def get_main_keyboard():
    keyboard = [
        [KeyboardButton("Scammer melden"), KeyboardButton("Trust melden")],
        [KeyboardButton("User prüfen")],
        [KeyboardButton("Löschung beantragen")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    total_reports = sum(user_data['count'] for list_type in reported_users for user_data in reported_users[list_type].values())
    await update.message.reply_text(
        f'👋 Willkommen beim Telegram Sicherheits-Bot! \n\n'
        f'Dieser Bot hilft Ihnen, sich vor Betrügern auf Telegram zu schützen. 🚫🔒 \n'
        f'Bitte beachten Sie, dass der Bot keine Garantie für die Sicherheit Ihrer Daten geben kann, aber er kann helfen Betrug zu verhindern. \n\n'
        f'Bisher wurden {total_reports} Meldungen erstellt.\n\n'
        f'Wählen Sie eine der folgenden Optionen:',
        reply_markup=get_main_keyboard()
    )

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
            keyboard = [
                [KeyboardButton("Daten aktualisieren")],
                [KeyboardButton("Erneut melden")]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard)
            await update.message.reply_text("Wählen Sie eine Option:", reply_markup=reply_markup)
            return UPDATING_USER

        await update.message.reply_text("Bitte geben Sie den vollständigen Namen des ausgewählten Nutzers ein:",
                                        reply_markup=ReplyKeyboardRemove())
        return WAITING_FOR_FULL_NAME
    else:
        await update.message.reply_text("Kein Benutzer ausgewählt. Bitte versuchen Sie es erneut.",
                                        reply_markup=get_main_keyboard())
        return ConversationHandler.END

async def check_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_shared = update.message.user_shared
    if user_shared:
        selected_user_id = user_shared.user_id

        if str(selected_user_id) in reported_users["scammers"]:
            user_data = reported_users["scammers"][str(selected_user_id)]
            message = (
                f"__**⚠️ Scammerliste ⚠️**__\n\n"
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
                f"__**✅ Trustliste ✅**__\n"
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
        await update.message.reply_text("Bitte geben Sie den vollständigen Namen des ausgewählten Nutzers ein:",
                                        reply_markup=ReplyKeyboardRemove())
        return WAITING_FOR_FULL_NAME
    elif choice == "Erneut melden":
        await update.message.reply_text("Bitte geben Sie den Meldegrund an:", reply_markup=ReplyKeyboardRemove())
        return WAITING_FOR_REASON
    else:
        await update.message.reply_text("Ungültige Auswahl. Bitte versuchen Sie es erneut.",
                                        reply_markup=get_main_keyboard())
        return ConversationHandler.END

async def receive_full_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    full_name = update.message.text or "Kein vollständiger Name angegeben"
    reported_user_id = context.user_data['reported_user_id']
    report_type = context.user_data['report_type']

    current_time = datetime.now().isoformat()
    if str(reported_user_id) not in reported_users[report_type]:
        # Initialisiere den Zähler auf 1, wenn der Benutzer zum ersten Mal gemeldet wird
        reported_users[report_type][str(reported_user_id)] = {
            "link": f"tg://user?id={reported_user_id}",
            "full_name": full_name,
            "username": "",
            "reason": "",
            "reported_by": update.effective_user.id,
            "first_reported_at": current_time,
            "last_reported_at": current_time,
            "count": 0  # Zähler auf 0 initialisieren
        }

    keyboard = [
        [KeyboardButton("Überspringen")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Bitte geben Sie den Benutzernamen des ausgewählten Nutzers ein (oder wählen Sie 'Überspringen'):",
        reply_markup=reply_markup)

    return WAITING_FOR_USERNAME

async def receive_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text == "Überspringen":
        username = "Nicht vorhanden"
    else:
        username = update.message.text or "Nicht vorhanden"

    reported_user_id = context.user_data['reported_user_id']
    report_type = context.user_data['report_type']

    reported_users[report_type][str(reported_user_id)]["username"] = username

    await update.message.reply_text("Bitte geben Sie nun den Meldegrund an:", reply_markup=ReplyKeyboardRemove())

    return WAITING_FOR_REASON

async def receive_reason(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reason = update.message.text
    reported_user_id = context.user_data['reported_user_id']
    report_type = context.user_data['report_type']

    if str(reported_user_id) in reported_users[report_type]:
        reported_users[report_type][str(reported_user_id)]["reason"] = reason
        reported_users[report_type][str(reported_user_id)]["last_reported_at"] = datetime.now().isoformat()
        reported_users[report_type][str(reported_user_id)]["count"] += 1  # Erhöhe den Zähler um 1

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
    support_message = f"Löschanfrage erhalten:\n{update.message.text}"
    sent_message = await context.bot.send_message(chat_id=SUPPORT_GROUP_ID, text=support_message)
    support_message_mapping[sent_message.message_id] = update.effective_user.id

    await update.message.reply_text("Ihr Löschantrag wurde eingereicht.", reply_markup=get_main_keyboard())
    return ConversationHandler.END

async def handle_support_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat_id == int(SUPPORT_GROUP_ID):
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

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    await update.message.reply_text("Ein unerwarteter Fehler ist aufgetreten. Bitte versuchen Sie es später erneut.")
