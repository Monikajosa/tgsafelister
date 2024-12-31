from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from .report import start_report
from .check import start_check

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
        return ConversationHandler.END
