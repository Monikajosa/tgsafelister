import os
from dotenv import load_dotenv

load_dotenv()

# Laden des Tokens aus Umgebungsvariablen oder direkt setzen
TOKEN = os.getenv('TELEGRAM_TOKEN', 'your-telegram-bot-token')
SUPPORT_GROUP_ID = os.getenv('SUPPORT_GROUP_ID', 'your-support-group-id')
OWNER_ID = os.getenv("OWNER_ID")
