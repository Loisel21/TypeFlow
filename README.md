# TypeFlow

TypeFlow is a Windows desktop voice dictation app for writing in any application with a global hotkey.

Built as a local-first MVP inspired by tools like Voicely:

- global dictation hotkey
- microphone capture
- local speech-to-text with Whisper
- insertion into the active Windows app
- background / tray workflow
- formatting modes for different writing contexts

## What It Does

TypeFlow lets you:

- dictate into any text field on Windows
- keep the app in the background while working
- switch between `normal`, `email`, `chat`, and `code` output modes
- use spoken formatting commands like punctuation and line breaks
- choose between direct typing and clipboard-based insertion

## Current Features

- global hotkey: `Ctrl+Shift+Space`
- local transcription with `faster-whisper`
- insertion into the previously active window
- tray app for background usage
- settings window with saved preferences
- log file for debugging focus and insertion
- output modes:
  - `normal`
  - `email`
  - `chat`
  - `code`
- spoken commands:
  - `Punkt`
  - `Komma`
  - `Fragezeichen`
  - `Ausrufezeichen`
  - `Doppelpunkt`
  - `Semikolon`
  - `neue Zeile`
  - `neuer Absatz`
  - `Tab`

## Roadmap

Planned next steps:

1. personal dictionary for names and domain-specific terms
2. snippets / reusable text blocks
3. richer voice actions like deleting or sending
4. optional cloud mode
5. packaged Windows `.exe`

## Requirements

- Windows 10 or 11
- Python 3.12+
- microphone access

## Setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run

```powershell
python main.py
```

Or on Windows:

```powershell
.\start.ps1
```

## Usage

1. Start TypeFlow.
2. Click into any text field.
3. Press `Ctrl+Shift+Space`.
4. Speak naturally.
5. Press `Ctrl+Shift+Space` again.
6. TypeFlow transcribes and inserts the text into the active app.
7. Optionally send the window into the background and continue from the tray.

## Output Modes

- `normal`: general-purpose sentence formatting
- `email`: cleaner, more formal output
- `chat`: lighter conversational formatting
- `code`: direct output with support for line breaks and tabs

## Spoken Formatting Example

Input:

```text
hallo team komma neue zeile bitte testet den build punkt
```

Output:

```text
Hallo team,
Bitte testet den build.
```

## Logs

TypeFlow writes logs to:

```text
logs/typeflow.log
```

Useful for debugging:

- remembered target window
- active window during insertion
- insertion mode used
- focus or paste issues

## Project Structure

- `main.py`: application entry point
- `typeflow/app.py`: application workflow
- `typeflow/hotkey.py`: global hotkey handling
- `typeflow/recorder.py`: microphone recording
- `typeflow/transcriber.py`: Whisper transcription
- `typeflow/inserter.py`: text insertion into Windows apps
- `typeflow/ui.py`: desktop UI
- `typeflow/tray.py`: system tray integration
- `typeflow/logger.py`: console and file logging
- `typeflow/formatter.py`: output modes and spoken commands
- `typeflow/config.py`: persisted settings

## Status

TypeFlow is currently an MVP focused on reliable dictation and insertion on Windows.
