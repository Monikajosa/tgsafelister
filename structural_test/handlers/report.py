from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButtonRequestUser
from telegram.ext import ContextTypes, ConversationHandler
from .utils import load_data, save_data, get_main_keyboard  # Stellen Sie sicher, dass diese Funktionen in utils.py definiert sind
from datetime import datetime
from telegram.helpers import escape_markdown

reported_users = load_data()

SELECTING_USER, WAITING_FOR_FULL_NAME, WAITING_FOR_USERNAME, WAITING_FOR_REASON, UPDATING_USER = range(5)

async def start_report(update: Update, context: ContextTypes.DEFAULT_TYPE, report_type: str) -> int:
    context.user_data['report_type'] = report_type
    other_report_type = "trusted" if report_type == "scammers" else "scammers"
    
    # Überprüfen, ob der Benutzer bereits in der anderen Liste vorhanden ist
    if str(update.message.from_user.id) in reported_users[other_report_type]:
        await update.message.reply_text(
            f"Der Benutzer ist bereits in der {other_report_type[:-1]}-Liste gemeldet und kann nicht erneut gemeldet werden.",
            reply_markup=get_main_keyboard()
        )
        return ConversationHandler.END
    
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

async def user_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_shared = update.message.user_shared
    if user_shared:
        selected_user_id = user_shared.user_id
        context.user_data['reported_user_id'] = selected_user_id
        report_type = context.user_data['report_type']
        other_report_type = "trusted" if report_type == "scammers" else "scammers"

        # Überprüfen, ob der Benutzer bereits in der anderen Liste vorhanden ist
        if str(selected_user_id) in reported_users[other_report_type]:
            await update.message.reply_text(
                f"Der Benutzer ist bereits in der {other_report_type[:-1]}-Liste gemeldet und kann nicht erneut gemeldet werden.",
                reply_markup=get_main_keyboard()
            )
            return ConversationHandler.END

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

async def receive_full_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    full_name = update.message.text or "Kein vollständiger Name angegeben"
    reported_user_id = context.user_data['reported_user_id']
    report_type = context.user_data['report_type']

    current_time = datetime.now().isoformat()
    if str(reported_user_id) not in reported_users[report_type]:
        reported_users[report_type][str(reported_user_id)] = {
            "link": f"tg://user?id={reported_user_id}",
            "full_name": full_name,
            "username": "",
            "reason": "",
            "reported_by": update.effective_user.id,
            "first_reported_at": current_time,
            "last_reported_at": current_time,
            "count": 0
        }

    keyboard = [
        [KeyboardButton("Überspringen")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Bitte geben Sie den __@Benutzernamen__ des ausgewählten Nutzers ein (oder wählen Sie 'Überspringen'):",
        reply_markup=reply_markup)

    return WAITING_FOR_USERNAME

async def receive_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    username = "Nicht vorhanden" if update.message.text == "Überspringen" else update.message.text or "Nicht vorhanden"
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
        reported_users[report_type][str(reported_user_id)]["count"] += 1

    await update.message.reply_text(f"Benutzer wurde erfolgreich als {report_type[:-1]} gemeldet.",
                                    reply_markup=get_main_keyboard())

    save_data()

    return ConversationHandler.END

async def handle_update_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    choice = update.message.text
    if choice == "Daten aktualisieren":
        await update.message.reply_text("Bitte geben Sie den vollständigen Namen des Nutzers ein:",
                                        reply_markup=ReplyKeyboardRemove())
        return WAITING_FOR_FULL_NAME
    elif choice == "Erneut melden":
        await update.message.reply_text("Bitte geben Sie den Meldegrund an:", reply_markup=ReplyKeyboardRemove())
        return WAITING_FOR_REASON
    else:
        await update.message.reply_text("Ungültige Auswahl. Bitte versuchen Sie es erneut.",
                                        reply_markup=get_main_keyboard())
        return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Meldung abgebrochen.", reply_markup=get_main_keyboard())
    return ConversationHandler.END
