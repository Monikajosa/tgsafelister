# tgsafelister

Hauptmenü
- "Safelist"
- "Blacklist (Scamer)"
- "Meldung erstellen"
- "Sprache wählen" (es soll Deutsch und Englisch geben. Standard soll der bot auf deutsch sein, jegliche Texte werden über zwei Sprachdateien gemanaged)
- "Support"

Funktion der einzelnen Menüs:

"Safelist" :
- Zeigt alle gemeldeten User mit Name inkl ID und sofern vorhanden auch den Benutzernamen. Auch die Variable 'countsafelist' soll angezeigt werden. Variable für "Safelist" ist 'safeuser'

"Blacklist (Scamer)" :
- Zeigt gemeldeten User mit Name inkl ID und sofern vorhanden auch den Benutzernamen. Auch die Variable 'countscamer' soll angezeigt werden. Variable für "Blacklist (Scamer)" ist 'scamer'

"Meldung erstellen"
- Benutzer bekommt ein "Kontakt auswählen" angezeigt bei dem er den User welchen er melden möchte suchen bzw. auswählen kann. Der Bot zeigt dann den ausgewählten Kontakt zur Bestätigung an und verarbeitet.
  - nachdem weiterleiten bekommt der User die Anfrage ob er den gemeldeten User der "Safelist" als 'safeuser' oder der "Blacklist (Scamer)" als 'scamer' hinzufügen möchte. Danach soll eine Abfrage erfolgen bei dem der zu meldende Nutzer sowie die gewünschte Deklaration angezeigt und abgefragt wird ob die Angaben stimmen. 
Nach Zustimmung -> Daten entsprechend in einer Datenbank speichern und für den Abruf über "Safelist" oder "Blacklist (Scamer)" vorbereiten. 
Nach ablehnen wieder zurück ins Hauptmenü und nichts speichern. 

Die gespeicherten Daten sollen immer die Daten passend zu den gespeicherten User ID aktualisieren wenn die jeweilige Abfrage Blacklist oder Safelist ausgeführt wird. sprich den Namen und Benutzernamen.

Die Datenbank soll die oben genannten Daten speichern. Ebenso soll erfasst werden wie viele Meldungen je User erfolgt sind über variable 'countscamer' sowie 'countsafelist' und je Liste mit ausgegeben werden. 

Sicherheit:

- Relevante Daten sollen in der .env gespeichert werden

- Jeder User darf mit seiner ID nur einmal die Selbe ID als 'safeuser' oder 'blacklist' innerhalb von 24h melden. Möchte er einen von ihm bereits gemeldeten User erneut melden bekommt er die Meldung das er den User bereits gemeldet hat und ein erneutes melden nicht als neue Meldung gewertet wird. 
- User können sich nicht selbst melden. Und sollte per Fehlermeldung einen Hinweis erhalten. Das dies gegen die bot Richtlinien geht.

- Die gemeldeten User sollen bei gleicher Anzahl an Meldungen in 'safeuser' oder 'blacklist' angezeigt werden. Hat ein Datensatz von 'safeuser' oder 'blacklist' mehr Meldungen wird der User nur noch in der Liste mit mehr Meldungen angezeigt.

Datensicherung:

- Die Daten sollen dauerhaft gespeichert werden und auch nach einem bot Neustart verfügbar sein. 

Verhalten des Bots:

- In der Gruppe in welcher er aktiv ist:
Per /safelist wird die Safelist ausgegeben
Per /blacklist wird die Blacklist ausgegeben

Im privaten Chat:

- Menu wie oben als Hauptmenü beschrieben. 

"Support" :

- Bot zeigt kurze Hilfestellung zur Benutzung an.
- Button Support kontaktieren.
- Im bot Menü soll es möglich sein das man dem Support schreibt. Nachrichten welche dann im Bot Menü geschrieben werden sollen in einer privaten Gruppe mit Verweis auf die User ID gepostet werden. Per reply auf die entsprechende Nachricht soll dem User geantwortet werden können.

Private Gruppe für bot Support:
- Nachrichten erhalten welche über den bot übermittelt werden.
- in der privaten Gruppe soll der bot auf Befehle reagieren.
- /del 'ID' , die erhält der bot diesen Befehl prüft er die Datenbank auf einen Eintrag mit der ID und löscht alle Einträge mit dieser ID
- /send 'Nachricht' , der bot sendet in allen Gruppen in denen er aktiv ist eine Nachricht. 

Plattform:

- Raspberry Pi 