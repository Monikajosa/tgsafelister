import json
from telegram import KeyboardButton, ReplyKeyboardMarkup

def load_data():
    try:
        with open('reported_users.json', 'r') as f:
            data = json.load(f)
            print("DEBUG: Daten geladen:", data)  # Debug-Ausgabe
            return data
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print("DEBUG: Fehler beim Laden der Daten:", e)  # Debug-Ausgabe
        return {"scammers": {}, "trusted": {}}

def save_data(reported_users):
    try:
        with open('reported_users.json', 'w') as f:
            json.dump(reported_users, f, indent=4)
            print("DEBUG: Daten gespeichert:", reported_users)  # Debug-Ausgabe
    except Exception as e:
        print("DEBUG: Fehler beim Speichern der Daten:", e)  # Debug-Ausgabe

def get_main_keyboard():
    keyboard = [
        [KeyboardButton("Scammer melden"), KeyboardButton("Trust melden")],
        [KeyboardButton("User prüfen")],
        [KeyboardButton("Löschung beantragen")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def escape_markdown(text):
    """Escapes markdown special characters."""
    escape_chars = r"\_*[]()~`>#+-=|{}.!"
    return ''.join(f'\\{char}' if char in escape_chars else char for char in text)
