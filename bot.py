import os
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext
import sqlite3
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Telegram Bot Token and Support Group ID
TOKEN = os.getenv("TELEGRAM_TOKEN")
SUPPORT_GROUP_ID = os.getenv("SUPPORT_GROUP_ID")

# Load language files
with open('de.json', 'r') as f:
    lang_de = json.load(f)
with open('en.json', 'r') as f:
    lang_en = json.load(f)

# Set default language to German
language = lang_de

def get_db_connection():
    conn = sqlite3.connect('users.db')
    return conn

def set_language(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    global language
    language_code = query.data.split('_')[1]
    if language_code == 'de':
        language = lang_de
    else:
        language = lang_en
    query.edit_message_text(text=language["language_set"].format(language=language_code.capitalize()))
    main_menu(update, context)

def start(update: Update, context: CallbackContext) -> None:
    chat_type = update.message.chat.type
    print(f"Chat Type: {chat_type}")
    if chat_type == 'private':
        update.message.reply_text(language["welcome"], reply_markup=main_menu_keyboard())
    else:
        update.message.reply_text("Dieser Befehl ist nur im privaten Chat verfügbar.")

def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton('Safelist', callback_data='safelist')],
        [InlineKeyboardButton('Blacklist (Scamer)', callback_data='blacklist')],
        [InlineKeyboardButton('Meldung erstellen', callback_data='create_report')],
        [InlineKeyboardButton('Sprache wählen', callback_data='choose_language')],
        [InlineKeyboardButton('Support', callback_data='support')],
    ]
    return InlineKeyboardMarkup(keyboard)

def main_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text=language["main_menu"], reply_markup=main_menu_keyboard())

def safelist(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM safeuser')
    safe_users = c.fetchall()
    response = language["safelist"] + "\n"
    for user in safe_users:
        response += f"Name: {user[2]}, ID: {user[1]}, Username: {user[3]}, Meldungen: {user[4]}\n"
    conn.close()
    query.edit_message_text(text=response, reply_markup=main_menu_keyboard())

def blacklist(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM scamer')
    scamer_users = c.fetchall()
    response = language["blacklist"] + "\n"
    for user in scamer_users:
        response += f"Name: {user[2]}, ID: {user[1]}, Username: {user[3]}, Meldungen: {user[4]}\n"
    conn.close()
    query.edit_message_text(text=response, reply_markup=main_menu_keyboard())

def create_report(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text=language["create_report"])

def handle_report(update: Update, context: CallbackContext):
    reported_id = update.message.text
    reporter_id = update.message.from_user.id
    if reporter_id == int(reported_id):
        update.message.reply_text(language["self_report_error"])
        return main_menu(update, context)
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM reports WHERE reporter_id = ? AND reported_id = ? AND timestamp >= datetime("now", "-1 day")', (reporter_id, reported_id))
    if c.fetchone():
        update.message.reply_text(language["duplicate_report_error"])
        conn.close()
        return main_menu(update, context)
    context.user_data['reported_id'] = reported_id
    keyboard = [
        [InlineKeyboardButton('Safelist', callback_data='report_safelist')],
        [InlineKeyboardButton('Blacklist (Scamer)', callback_data='report_blacklist')],
    ]
    conn.close()
    update.message.reply_text(language["create_report"], reply_markup=InlineKeyboardMarkup(keyboard))

def report_safelist(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    reported_id = context.user_data['reported_id']
    reporter_id = update.callback_query.from_user.id
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('INSERT INTO reports (reporter_id, reported_id, report_type) VALUES (?, ?, ?)', (reporter_id, reported_id, 'safeuser'))
    c.execute('INSERT OR IGNORE INTO safeuser (user_id, countsafelist) VALUES (?, 0)', (reported_id,))
    c.execute('UPDATE safeuser SET countsafelist = countsafelist + 1 WHERE user_id = ?', (reported_id,))
    conn.commit()
    conn.close()
    query.edit_message_text(text=language["report_success"].format(list="Safelist"))
    return main_menu(update, context)

def report_blacklist(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    reported_id = context.user_data['reported_id']
    reporter_id = update.callback_query.from_user.id
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('INSERT INTO reports (reporter_id, reported_id, report_type) VALUES (?, ?, ?)', (reporter_id, reported_id, 'scamer'))
    c.execute('INSERT OR IGNORE INTO scamer (user_id, countscamer) VALUES (?, 0)', (reported_id,))
    c.execute('UPDATE scamer SET countscamer = countscamer + 1 WHERE user_id = ?', (reported_id,))
    conn.commit()
    conn.close()
    query.edit_message_text(text=language["report_success"].format(list="Blacklist"))
    return main_menu(update, context)

def choose_language(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    keyboard = [
        [InlineKeyboardButton('Deutsch', callback_data='language_de')],
        [InlineKeyboardButton('Englisch', callback_data='language_en')],
    ]
    query.edit_message_text(text=language["choose_language"], reply_markup=InlineKeyboardMarkup(keyboard))

def support(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text=language["support"])

def handle_support_message(update: Update, context: CallbackContext):
    message = update.message.text
    user_id = update.message.from_user.id
    context.bot.send_message(chat_id=SUPPORT_GROUP_ID, text=f"Support-Anfrage von {user_id}:\n\n{message}")

def delete_user(update: Update, context: CallbackContext):
    user_id = context.args[0]
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('DELETE FROM safeuser WHERE user_id = ?', (user_id,))
    c.execute('DELETE FROM scamer WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()
    context.bot.send_message(chat_id=update.message.chat_id, text=f"User mit ID {user_id} wurde gelöscht.")

def send_message(update: Update, context: CallbackContext):
    message = ' '.join(context.args)
    for chat_id in context.bot_data['active_chats']:
        context.bot.send_message(chat_id=chat_id, text=message)

def group_safelist(update: Update, context: CallbackContext):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM safeuser')
    safe_users = c.fetchall()
    response = language["safelist"] + "\n"
    for user in safe_users:
        response += f"Name: {user[2]}, ID: {user[1]}, Username: {user[3]}, Meldungen: {user[4]}\n"
    conn.close()
    update.message.reply_text(text=response)

def group_blacklist(update: Update, context: CallbackContext):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM scamer')
    scamer_users = c.fetchall()
    response = language["blacklist"] + "\n"
    for user in scamer_users:
        response += f"Name: {user[2]}, ID: {user[1]}, Username: {user[3]}, Meldungen: {user[4]}\n"
    conn.close()
    update.message.reply_text(text=response)

def main():
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Command handlers for private chat
    dispatcher.add_handler(CommandHandler("start", start, filters=Filters.chat_type.private))
    
    # Command handlers for groups
    dispatcher.add_handler(CommandHandler("safelist", group_safelist, filters=Filters.chat_type.groups))
    dispatcher.add_handler(CommandHandler("blacklist", group_blacklist, filters=Filters.chat_type.groups))

    # Admin command handlers for group
    dispatcher.add_handler(CommandHandler("del", delete_user, filters=Filters.chat_type.groups, pass_args=True))
    dispatcher.add_handler(CommandHandler("send", send_message, filters=Filters.chat_type.groups, pass_args=True))

    # Callback query handler
    dispatcher.add_handler(CallbackQueryHandler(main_menu, pattern='main_menu'))
    dispatcher.add_handler(CallbackQueryHandler(safelist, pattern='safelist'))
    dispatcher.add_handler(CallbackQueryHandler(blacklist, pattern='blacklist'))
    dispatcher.add_handler(CallbackQueryHandler(create_report, pattern='create_report'))
    dispatcher.add_handler(CallbackQueryHandler(report_safelist, pattern='report_safelist'))
    dispatcher.add_handler(CallbackQueryHandler(report_blacklist, pattern='report_blacklist'))
    dispatcher.add_handler(CallbackQueryHandler(choose_language, pattern='choose_language'))
    dispatcher.add_handler(CallbackQueryHandler(set_language, pattern='language_'))

    # Message handler for private chat
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command & Filters.chat_type.private, handle_report))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command & Filters.chat_type.private, handle_support_message))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
