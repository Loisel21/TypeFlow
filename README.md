# VoiceSpeech

Windows-Desktop-App fuer systemweites Diktieren. Das Projekt ist als MVP fuer eine App im Stil von Voicely aufgebaut:

- globaler Hotkey
- Aufnahme ueber das Mikrofon
- lokale Speech-to-Text-Transkription
- Einfuegen des Texts in die aktive Windows-App

## MVP-Status

Aktuell enthalten:

- `Ctrl+Shift+Space` startet und stoppt die Aufnahme
- lokale Transkription mit `faster-whisper`
- automatisches Einfuegen in aktive Windows-Apps
- Tray-App fuer Hintergrundbetrieb
- Log-Datei fuer Einfuegen und Fehlerdiagnose
- Ausgabe-Modi: `normal`, `email`, `chat`, `code`
- erste Sprachbefehle fuer Zeichensetzung und Umbrueche
- Settings-Fenster mit speicherbaren Optionen
- kleines Desktop-Fenster mit Statusanzeige

Noch nicht enthalten:

- persoenliches Lexikon
- Snippets / Textbausteine
- KI-Nachbearbeitung fuer perfekte E-Mails
- echter Privacy-vs-Cloud-Modus
- Installer / Auto-Start / Update-Mechanismus

## Voraussetzungen

- Windows 10 oder 11
- Python 3.12+
- Mikrofon

## Installation

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Start

```powershell
python main.py
```

Oder unter Windows direkt:

```powershell
.\start.ps1
```

## Bedienung

1. App starten
2. In ein beliebiges Textfeld klicken
3. `Ctrl+Shift+Space` druecken und sprechen
4. Den gleichen Hotkey erneut druecken
5. Der erkannte Text wird automatisch eingefuegt
6. Optional das Fenster mit "In den Hintergrund" ausblenden und nur ueber das Tray weiterlaufen lassen

## Modi

- `normal`: Standardtext mit Satzlogik
- `email`: etwas formeller mit sauberer Satzlogik
- `chat`: lockerer Text ohne erzwungenen Abschlusspunkt
- `code`: direkte Ausgabe mit Zeilenumbruechen und Tabs

## Sprachbefehle

Unterstuetzt aktuell:

- `Punkt`
- `Komma`
- `Fragezeichen`
- `Ausrufezeichen`
- `Doppelpunkt`
- `Semikolon`
- `neue Zeile`
- `neuer Absatz`
- `Tab`

Beispiel:

```text
hallo team komma neue zeile bitte testet den build punkt
```

## Logs

Die App schreibt ein Log nach:

- `logs/voicespeech.log`

Dort siehst du unter anderem:

- welches Ziel-Fenster gemerkt wurde
- ob Einfuegen ueber Zwischenablage oder Tippen lief
- Fehler beim Fokus oder Paste-Vorgang

## Architektur

- `voicespeech/app.py`: Anwendungslogik und Workflow
- `voicespeech/hotkey.py`: globaler Hotkey
- `voicespeech/recorder.py`: Mikrofonaufnahme
- `voicespeech/transcriber.py`: lokale STT-Pipeline
- `voicespeech/inserter.py`: Einfuegen in aktive App
- `voicespeech/ui.py`: kleines Tk-Frontend
- `voicespeech/tray.py`: Windows-Systemtray
- `voicespeech/logger.py`: Log-Datei und Konsolen-Logging
- `voicespeech/formatter.py`: Ausgabe-Modi und Sprachbefehle

## Naechste sinnvolle Schritte

1. persoenliches Lexikon und Fachbegriffe
2. Snippets / Textbausteine
3. echte Voice-Aktionen wie "letzten Satz loeschen" oder "Nachricht senden"
4. optionaler Cloud-Modus mit OpenAI oder Deepgram
5. Windows-Build als `.exe` mit PyInstaller
