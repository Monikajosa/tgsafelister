from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButtonRequestUser
from telegram.ext import ContextTypes, ConversationHandler
from datetime import datetime
import json

# Zustände für den ConversationHandler
SELECTING_USER, WAITING_FOR_FULL_NAME, WAITING_FOR_USERNAME, WAITING_FOR_REASON, UPDATING_USER = range(5)

# Funktion zum Laden der Daten
def load_data():
    try:
        with open('reported_users.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"DEBUG: Fehler beim Laden der Daten: {e}")
        return {"scammers": {}, "trusted": {}}

# Funktion zum Speichern der Daten
def save_data(data):
    with open('reported_users.json', 'w') as f:
        json.dump(data, f, indent=4)

# Funktion zum Zählen der Gesamtmeldungen
def get_total_reports(data):
    return sum(user_data['count'] for list_type in data for user_data in data[list_type].values())

# Funktion zum Abrufen der Haupttastatur
def get_main_keyboard():
    keyboard = [
        [KeyboardButton("Scammer melden"), KeyboardButton("Trust melden")],
        [KeyboardButton("User prüfen")],
        [KeyboardButton("Löschung beantragen")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Funktion zum Starten des Berichts
async def start_report(update: Update, context: ContextTypes.DEFAULT_TYPE, report_type: str) -> int:
    context.user_data['report_type'] = report_type
    context.user_data['reported_users'] = load_data()
    other_report_type = "trusted" if report_type == "scammers" else "scammers"
    
    reported_users = context.user_data['reported_users']  # Daten aus dem Kontext laden
    print(f"DEBUG: Start report - Geladene Daten: {reported_users}")
    
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

# Funktion zum Auswählen eines Benutzers
async def user_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_shared = update.message.user_shared
    if user_shared:
        selected_user_id = user_shared.user_id
        context.user_data['reported_user_id'] = selected_user_id
        report_type = context.user_data['report_type']
        other_report_type = "trusted" if report_type == "scammers" else "scammers"

        reported_users = context.user_data['reported_users']  # Daten aus dem Kontext laden
        print(f"DEBUG: User selected - Geladene Daten: {reported_users}")

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

# Funktion zum Empfangen des vollständigen Namens
async def receive_full_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    full_name = update.message.text or "Kein vollständiger Name angegeben"
    reported_user_id = context.user_data['reported_user_id']
    report_type = context.user_data['report_type']

    reported_users = context.user_data['reported_users']  # Daten aus dem Kontext laden
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
    else:
        reported_users[report_type][str(reported_user_id)]["full_name"] = full_name

    print(f"DEBUG: Full name received - Aktualisierte Daten: {reported_users}")

    keyboard = [
        [KeyboardButton("Überspringen")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Bitte geben Sie den __@Benutzernamen__ des ausgewählten Nutzers ein (oder wählen Sie 'Überspringen'):",
        reply_markup=reply_markup)

    return WAITING_FOR_USERNAME

# Funktion zum Empfangen des Benutzernamens
async def receive_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    username = "Nicht vorhanden" if update.message.text == "Überspringen" else update.message.text or "Nicht vorhanden"
    reported_user_id = context.user_data['reported_user_id']
    report_type = context.user_data['report_type']

    reported_users = context.user_data['reported_users']  # Daten aus dem Kontext laden
    print(f"DEBUG: Username received - Geladene Daten: {reported_users}")

    if str(reported_user_id) in reported_users[report_type]:
        reported_users[report_type][str(reported_user_id)]["username"] = username

    print(f"DEBUG: Username set - Aktualisierte Daten: {reported_users}")

    await update.message.reply_text("Bitte geben Sie nun den Meldegrund an:", reply_markup=ReplyKeyboardRemove())

    return WAITING_FOR_REASON

# Funktion zum Empfangen des Grundes
async def receive_reason(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reason = update.message.text
    reported_user_id = context.user_data['reported_user_id']
    report_type = context.user_data['report_type']

    reported_users = context.user_data['reported_users']  # Daten aus dem Kontext laden
    print(f"DEBUG: Reason received - Geladene Daten: {reported_users}")
    
    if str(reported_user_id) in reported_users[report_type]:
        reported_users[report_type][str(reported_user_id)]["reason"] = reason
        reported_users[report_type][str(reported_user_id)]["last_reported_at"] = datetime.now().isoformat()
        reported_users[report_type][str(reported_user_id)]["count"] += 1

    print(f"DEBUG: Reason set - Daten vor dem Speichern: {reported_users}")
    context.user_data['reported_users'] = reported_users  # Aktualisierte Daten im Kontext speichern
    save_data(reported_users)  # Daten speichern
    print(f"DEBUG: Daten gespeichert: {reported_users}")

    total_reports = get_total_reports(reported_users)
    await update.message.reply_text(f"Benutzer wurde erfolgreich als {report_type[:-1]} gemeldet. Es gibt jetzt insgesamt {total_reports} Meldungen.",
                                    reply_markup=get_main_keyboard())

    return ConversationHandler.END

# Funktion zum Handhaben des Auswahlmenüs für Updates
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

# Funktion zum Abbrechen des Prozesses
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Meldung abgebrochen.", reply_markup=get_main_keyboard())
    return ConversationHandler.END

# Funktion zum Escapen von Markdown-Sonderzeichen
def escape_markdown(text):
    """Escapes markdown special characters."""
    escape_chars = r"\_*[]()~`>#+-=|{}.!"
    return ''.join(f'\\{char}' if char in escape_chars else char for char in text)
