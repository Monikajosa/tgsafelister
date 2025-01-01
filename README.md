```
tgsafelister/
├── bot.py
├── config.py
├── handlers.py
├── requirements.txt
├── .env
├── README.md
├── handlers/
│   ├── __init__.py
│   ├── start.py
│   ├── main_menu.py
│   ├── report.py
│   ├── check.py
│   ├── error_handler.py
│   ├── deletion.py
│   ├── support.py
│   ├── utils.py
│   ├── deletion_request.py
```


**Erläuterungen:**

- **bot.py**: Hauptdatei, die den Bot startet und die verschiedenen Handler konfiguriert.
- **config.py**: Konfigurationsdateien und Einstellungen, die Umgebungsvariablen laden.
- **handlers/**: Verzeichnis für alle Handlermodule.
  - **__init__.py**: Initialisierungsdatei für das Handlermodul.
  - **start.py**: Handler für den Start-Befehl.
  - **main_menu.py**: Handler für das Hauptmenü.
  - **report.py**: Handler für das Melden von Benutzern.
  - **check.py**: Handler für das Überprüfen von Benutzern.
  - **error_handler.py**: Handler für Fehlerbehandlung.
  - **deletion.py**: Handler für Löschanfragen.
  - **support.py**: Handler für Support-Nachrichten.
  - **utils.py**: Hilfsfunktionen und Utilities.
  - **deletion_request.py**: Handler für Löschanfragen von Benutzern.
- **handlers.py**: Datei, die alle Handler importiert und konfiguriert.
- **requirements.txt**: Liste der Abhängigkeiten des Projekts.
- **.env**: Datei, die Umgebungsvariablen enthält.
