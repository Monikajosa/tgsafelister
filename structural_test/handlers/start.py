import logging
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from handlers.utils import get_main_keyboard, load_data

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    reported_users = load_data()
    total_reports = sum(user_data['count'] for list_type in reported_users for user_data in reported_users[list_type].values())
    await update.message.reply_text(
        f'👋 Willkommen beim Telegram Sicherheits-Bot! \n\n'
        f'Dieser Bot hilft Ihnen, sich vor Betrügern auf Telegram zu schützen. 🚫🔒 \n'
        f'Bitte beachten Sie, dass der Bot keine Garantie für die Sicherheit Ihrer Daten geben kann, aber er kann helfen Betrug zu verhindern. \n\n'
        f'Bisher wurden {total_reports} Meldungen erstellt.\n\n'
        f'Wählen Sie eine der folgenden Optionen:',
        reply_markup=get_main_keyboard()
    )
