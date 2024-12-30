import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
from config import TOKEN, SUPPORT_GROUP_ID, OWNER_ID
from handlers import start, handle_main_menu, user_selected, check_user, handle_update_choice, receive_full_name, receive_username, receive_reason, cancel, receive_deletion_info, handle_support_message, error_handler, delete_user
from handlers import SELECTING_USER, WAITING_FOR_FULL_NAME, WAITING_FOR_USERNAME, WAITING_FOR_REASON, UPDATING_USER, WAITING_FOR_DELETION_INFO, CHECKING_LIST

# Logging konfigurieren
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

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
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_support_message))
    application.add_handler(CommandHandler("del", delete_user))

    # Register the error handler
    application.add_error_handler(error_handler)

    application.run_polling()

if __name__ == '__main__':
    main()
