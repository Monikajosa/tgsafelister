# tgsafelister

## Inhaltsverzeichnis
1. [Einführung](#einführung)
2. [Hauptmenü](#hauptmenü)
    - [Safelist](#safelist)
    - [Blacklist (Scamer)](#blacklist-scamer)
    - [Meldung erstellen](#meldung-erstellen)
    - [Sprache wählen](#sprache-wählen)
    - [Support](#support)
3. [Datenbank](#datenbank)
4. [Sicherheit](#sicherheit)
5. [Datensicherung](#datensicherung)
6. [Verhalten des Bots](#verhalten-des-bots)
    - [In der Gruppe](#in-der-gruppe)
    - [Im privaten Chat](#im-privaten-chat)
7. [Support-Gruppe](#support-gruppe)
8. [Plattform](#plattform)

## Einführung
tgsafelister ist ein Telegram-Bot, der es ermöglicht, User auf eine Safelist oder Blacklist zu setzen. Der Bot unterstützt dabei verschiedene Funktionen und Einstellungen, um die Nutzung zu erleichtern.

## Hauptmenü

### Safelist
- Zeigt alle gemeldeten User mit Name inkl. ID und, sofern vorhanden, auch den Benutzernamen.
- Variable für "Safelist" ist `safeuser`.
- Zeigt die Anzahl der Meldungen (`countsafelist`).

### Blacklist (Scamer)
- Zeigt gemeldete User mit Name inkl. ID und, sofern vorhanden, auch den Benutzernamen.
- Variable für "Blacklist (Scamer)" ist `scamer`.
- Zeigt die Anzahl der Meldungen (`countscamer`).

### Meldung erstellen
- Benutzer kann einen User melden, indem er einen Kontakt auswählt und bestätigt.
- Der gemeldete User kann der "Safelist" (`safeuser`) oder der "Blacklist (Scamer)" (`scamer`) hinzugefügt werden.
- Nach Zustimmung werden die Daten in einer Datenbank gespeichert.

### Sprache wählen
- Benutzer kann zwischen Deutsch und Englisch wählen.
- Standardmäßig ist der Bot auf Deutsch eingestellt.
- Texte werden über zwei Sprachdateien verwaltet.

### Support
- Bot zeigt eine kurze Hilfestellung zur Benutzung an.
- Button "Support kontaktieren" ermöglicht es, dem Support direkt zu schreiben.

## Datenbank
- Speichert alle relevanten Daten der gemeldeten User.
- Aktualisiert die Daten passend zur gespeicherten User-ID bei jeder Abfrage.
- Erfasst die Anzahl der Meldungen je User (`countscamer` und `countsafelist`).

## Sicherheit
- Relevante Daten werden in der `.env`-Datei gespeichert.
- Jeder User kann nur einmal alle 24 Stunden dieselbe ID melden.
- User können sich nicht selbst melden.
- Gemeldete User werden nach Anzahl der Meldungen sortiert angezeigt.

## Datensicherung
- Daten werden dauerhaft gespeichert und sind auch nach einem Bot-Neustart verfügbar.

## Verhalten des Bots

### In der Gruppe
- `/safelist` gibt die Safelist aus.
- `/blacklist` gibt die Blacklist aus.

### Im privaten Chat
- Hauptmenü wie oben beschrieben.

## Support-Gruppe
- wird in der .env definiert damit der Bot für den Support ausschließlich dort reagiert
- Nachrichten, die über den Bot übermittelt werden, erscheinen in einer privaten Gruppe. Per Reply kann den User geantwortet werden und die Antwort wird zurück an den Bot Chat übermittelt.
- Bot reagiert auf Befehle in der privaten Gruppe:
  - `/del 'ID'` löscht alle Einträge mit dieser ID.
  - `/send 'Nachricht'` sendet die Nachricht in allen Gruppen, in denen der Bot aktiv ist.

## Plattform
- Läuft auf einem Raspberry Pi.
- Sprache python
