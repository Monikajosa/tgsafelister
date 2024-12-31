import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
from handlers.start import start
from handlers.main_menu import handle_main_menu
from handlers.report import user_selected, receive_full_name, receive_username, receive_reason
from handlers.check import check_user
from handlers.error_handler import error_handler
from handlers.deletion import delete_user
from handlers.support import handle_support_message

# Logging konfigurieren
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    application = Application.builder().token("YOUR TOKEN HERE").build()

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & ~filters.COMMAND, handle_main_menu)],
        states={
            SELECTING_USER: [MessageHandler(filters.StatusUpdate.USER_SHARED, user_selected)],
            WAITING_FOR_FULL_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_full_name)],
            WAITING_FOR_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_username)],
            WAITING_FOR_REASON: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_reason)],
            CHECKING_LIST: [MessageHandler(filters.StatusUpdate.USER_SHARED, check_user)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_support_message))
    application.add_error_handler(error_handler)

    application.run_polling()

if __name__ == '__main__':
    main()
