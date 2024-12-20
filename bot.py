import os
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
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

# Dictionary to store user languages and support message mapping
user_languages = {}
support_message_mapping = {}

def get_db_connection():
    conn = sqlite3.connect('users.db')
    return conn

def set_language(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    language_code = query.data.split('_')[1]
    if language_code == 'de':
        user_languages[user_id] = lang_de
    else:
        user_languages[user_id] = lang_en
    query.edit_message_text(text=user_languages[user_id]["language_set"].format(language=language_code.capitalize()))
    main_menu(update, context)

def start(update: Update, context: CallbackContext) -> None:
    chat_type = update.message.chat.type
    user_id = update.message.from_user.id
    if user_id not in user_languages:
        user_languages[user_id] = language
    if chat_type == 'private':
        update.message.reply_text(user_languages[user_id]["welcome"], reply_markup=main_menu_keyboard(user_id))
    else:
        update.message.reply_text(user_languages[user_id]["private_chat_only"])

def main_menu_keyboard(user_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(user_languages[user_id]['safelist_button'], callback_data='safelist')],
        [InlineKeyboardButton(user_languages[user_id]['blacklist_button'], callback_data='blacklist')],
        [InlineKeyboardButton(user_languages[user_id]['report_button'], callback_data='create_report')],
        [InlineKeyboardButton(user_languages[user_id]['language_button'], callback_data='choose_language')],
        [InlineKeyboardButton(user_languages[user_id]['support_button'], callback_data='support')],
    ])

def main_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    query.edit_message_text(text=user_languages[user_id]["main_menu"], reply_markup=main_menu_keyboard(user_id))

def safelist(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id

    # Ensure user language is set
    if user_id not in user_languages:
        user_languages[user_id] = language

    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM safeuser')
    safe_users = c.fetchall()
    response = user_languages[user_id]["safelist"] + "\n"
    for user in safe_users:
        if user[3]:  # Benutzername vorhanden
            response += f"Name: [{user[2]}](https://t.me/{user[3]}), ID: {user[1]}, Username: [@{user[3]}](https://t.me/{user[3]}), Meldungen: {user[4]}\n"
        else:  # Kein Benutzername, stattdessen Benutzer-ID verwenden
            response += f"Name: [{user[2]}](https://t.me/{user[1]}), ID: {user[1]}, Profil: [Profil anzeigen](https://t.me/{user[1]}), Meldungen: {user[4]}\n"
    conn.close()
    
    # Only edit the message if the content has changed
    if query.message.text != response:
        query.edit_message_text(text=response, reply_markup=main_menu_keyboard(user_id), parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)

def blacklist(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id

    # Ensure user language is set
    if user_id not in user_languages:
        user_languages[user_id] = language

    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM scamer')
    scamer_users = c.fetchall()
    response = user_languages[user_id]["blacklist"] + "\n"
    for user in scamer_users:
        if user[3]:  # Benutzername vorhanden
            response += f"Name: [{user[2]}](https://t.me/{user[3]}), ID: {user[1]}, Username: [@{user[3]}](https://t.me/{user[3]}), Meldungen: {user[4]}\n"
        else:  # Kein Benutzername, stattdessen Benutzer-ID verwenden
            response += f"Name: [{user[2]}](https://t.me/{user[1]}), ID: {user[1]}, Profil: [Profil anzeigen](https://t.me/{user[1]}), Meldungen: {user[4]}\n"
    conn.close()

    # Only edit the message if the content has changed
    if query.message.text != response:
        query.edit_message_text(text=response, reply_markup=main_menu_keyboard(user_id), parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)

def create_report(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    query.edit_message_text(user_languages[user_id]["forward_message"])

def choose_language(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    keyboard = [
        [InlineKeyboardButton('Deutsch', callback_data='language_de')],
        [InlineKeyboardButton('English', callback_data='language_en')],
    ]
    query.edit_message_text(text=user_languages[user_id]["choose_language"], reply_markup=InlineKeyboardMarkup(keyboard))

def support(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    query.edit_message_text(text=user_languages[user_id]["support"])

def handle_forwarded_message(update: Update, context: CallbackContext):
    forwarded_from = update.message.forward_from
    user_id = update.message.from_user.id
    if forwarded_from:
        reported_id = forwarded_from.id
        reported_username = forwarded_from.username
        reported_name = forwarded_from.full_name

        context.user_data['reported_id'] = reported_id
        context.user_data['reported_username'] = reported_username
        context.user_data['reported_name'] = reported_name

        keyboard = [
            [InlineKeyboardButton(user_languages[user_id]['safelist_button'], callback_data='report_safelist')],
            [InlineKeyboardButton(user_languages[user_id]['blacklist_button'], callback_data='report_blacklist')],
        ]
        update.message.reply_text(user_languages[user_id]["choose_list"], reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        update.message.reply_text(user_languages[user_id]["invalid_forward_message"])

def report_safelist(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    reported_id = context.user_data['reported_id']
    reported_username = context.user_data['reported_username']
    reported_name = context.user_data['reported_name']
    reporter_id = update.callback_query.from_user.id
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('INSERT INTO reports (reporter_id, reported_id, report_type) VALUES (?, ?, ?)', (reporter_id, reported_id, 'safeuser'))
    c.execute('INSERT OR IGNORE INTO safeuser (user_id, countsafelist, username, name) VALUES (?, 0, ?, ?)', (reported_id, reported_username, reported_name))
    c.execute('UPDATE safeuser SET countsafelist = countsafelist + 1 WHERE user_id = ?', (reported_id,))
    conn.commit()
    conn.close()
    query.edit_message_text(text=user_languages[user_id]["report_success"].format(list=user_languages[user_id]["safelist_button"]))
    return main_menu(update, context)

def report_blacklist(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    reported_id = context.user_data['reported_id']
    reported_username = context.user_data['reported_username']
    reported_name = context.user_data['reported_name']
    reporter_id = update.callback_query.from_user.id
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('INSERT INTO reports (reporter_id, reported_id, report_type) VALUES (?, ?, ?)', (reporter_id, reported_id, 'scamer'))
    c.execute('INSERT OR IGNORE INTO scamer (user_id, countscamer, username, name) VALUES (?, 0, ?, ?)', (reported_id, reported_username, reported_name))
    c.execute('UPDATE scamer SET countscamer = countscamer + 1 WHERE user_id = ?', (reported_id,))
    conn.commit()
    conn.close()
    query.edit_message_text(text=user_languages[user_id]["report_success"].format(list=user_languages[user_id]["blacklist_button"]))
    return main_menu(update, context)

def handle_support_message(update: Update, context: CallbackContext):
    if update.message.chat_id == int(SUPPORT_GROUP_ID):
        # Message is from the support group
        if update.message.reply_to_message and update.message.reply_to_message.message_id in support_message_mapping:
            original_user_id = support_message_mapping[update.message.reply_to_message.message_id]
            context.bot.send_message(chat_id=original_user_id, text=update.message.text)
        else:
            context.bot.send_message(chat_id=update.message.chat_id, text="Keine zugeordnete Support-Anfrage gefunden.")
    else:
        # Message is from a user
        user_id = update.message.from_user.id
        sent_message = context.bot.send_message(chat_id=SUPPORT_GROUP_ID, text=f"Support-Anfrage von {user_id}:\n\n{update.message.text}")
        support_message_mapping[sent_message.message_id] = user_id

def delete_user(update: Update, context: CallbackContext):
    user_id = context.args[0]
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('DELETE FROM safeuser WHERE user_id = ?', (user_id,))
    c.execute('DELETE FROM scamer WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()
    context.bot.send_message(chat_id=update.message.chat_id, text=language["user_deleted"].format(user_id=user_id))

def send_message(update: Update, context: CallbackContext):
    message = ' '.join(context.args)
    for chat_id in context.bot_data['active_chats']:
        context.bot.send_message(chat_id=chat_id, text=message)

def group_safelist(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM safeuser')
    safe_users = c.fetchall()
    response = user_languages[user_id]["safelist"] + "\n"
    for user in safe_users:
        if user[3]:  # Benutzername vorhanden
            response += f"Name: [{user[2]}](https://t.me/{user[3]}), ID: {user[1]}, Username: [@{user[3]}](https://t.me/{user[3]}), Meldungen: {user[4]}\n"
        else:  # Kein Benutzername, stattdessen Benutzer-ID verwenden
            response += f"Name: [{user[2]}](https://t.me/{user[1]}), ID: {user[1]}, Profil: [Profil anzeigen](https://t.me/{user[1]}), Meldungen: {user[4]}\n"
    conn.close()
    update.message.reply_text(text=response, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)

def group_blacklist(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM scamer')
    scamer_users = c.fetchall()
    response = user_languages[user_id]["blacklist"] + "\n"
    for user in scamer_users:
        if user[3]:  # Benutzername vorhanden
            response += f"Name: [{user[2]}](https://t.me/{user[3]}), ID: {user[1]}, Username: [@{user[3]}](https://t.me/{user[3]}), Meldungen: {user[4]}\n"
        else:  # Kein Benutzername, stattdessen Benutzer-ID verwenden
            response += f"Name: [{user[2]}](https://t.me/{user[1]}), ID: {user[1]}, Profil: [Profil anzeigen](https://t.me/{user[1]}), Meldungen: {user[4]}\n"
    conn.close()
    update.message.reply_text(text=response, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)

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
    dispatcher.add_handler(CallbackQueryHandler(support, pattern='support'))

    # Message handler for forwarded messages
    dispatcher.add_handler(MessageHandler(Filters.forwarded & Filters.chat_type.private, handle_forwarded_message))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_support_message))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
