from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, KeyboardButtonRequestUser
from telegram.ext import ContextTypes, ConversationHandler
from .utils import load_data, get_main_keyboard, escape_markdown

CHECKING_LIST = range(1)

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

async def check_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_shared = update.message.user_shared
    if user_shared:
        selected_user_id = user_shared.user_id
        print(f"DEBUG: Überprüfe Benutzer-ID: {selected_user_id}")  # Debug-Ausgabe

        reported_users = load_data()  # Daten neu laden

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
