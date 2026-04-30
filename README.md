# TypeFlow

TypeFlow is a Windows desktop voice dictation app for writing in any application with a global hotkey.

Built as a local-first MVP inspired by tools like Voicely:

- global dictation hotkey
- microphone capture
- local speech-to-text with Whisper
- insertion into the active Windows app
- background / tray workflow
- formatting modes for different writing contexts
- personal replacements and snippets
- local-first privacy mode and text cleanup

## What It Does

TypeFlow lets you:

- dictate into any text field on Windows
- keep the app in the background while working
- switch between `normal`, `email`, `chat`, and `code` output modes
- use spoken formatting commands like punctuation and line breaks
- choose between direct typing and clipboard-based insertion
- maintain a personal lexicon for names, brands, and domain terms
- trigger reusable snippets by voice
- clean up filler words automatically
- optionally translate German -> English or English -> German before insertion
- stop dictation automatically after a short period of silence

## Current Features

- global hotkey: `Ctrl+Shift+Space`
- local transcription with `faster-whisper`
- insertion into the previously active window
- tray app for background usage
- settings window with saved preferences
- log file for debugging focus and insertion
- privacy mode toggle for local-first workflow
- automatic filler-word cleanup
- automatic stop after silence
- personal lexicon replacements
- voice-triggered snippets
- configurable translation mode:
  - `off`
  - `de_to_en`
  - `en_to_de`
- output modes:
  - `normal`
  - `email`
  - `chat`
  - `code`
- spoken commands currently support German and core English variants:
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

1. richer voice actions like deleting, selecting, or sending
2. better code dictation vocabulary
3. optional cloud enhancement mode
4. packaged Windows `.exe`
5. app icon, onboarding, and installer polish

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

## Translation

You can now choose a translation mode in Settings:

- `off`
- `de_to_en`
- `en_to_de`

The translation step runs after formatting and before insertion.

Example flow:

1. Dictate in German
2. TypeFlow transcribes and cleans up the text
3. TypeFlow translates it to English
4. The translated result is inserted into the active app

Note:

- the current translation feature uses an online translation service
- local dictation still works without translation
- if you want strict local-only behavior, keep translation set to `off`

## Automatic Stop

TypeFlow can stop recording automatically so you do not always need to press the hotkey a second time.

Settings available:

- `Stop recording automatically after silence`
- `Silence timeout (s)`
- `Max recording (s)`

Behavior:

- if speech is detected and then you stay quiet for the configured silence timeout, recording stops automatically
- if recording runs too long, it also stops at the configured maximum duration

## Personalization

TypeFlow now supports two Voicely-like personalization layers:

- `Lexicon replacements`: spoken phrase => preferred written phrase
- `Snippets`: spoken trigger => inserted reusable text

Examples:

```text
type flow => TypeFlow
open ai => OpenAI
```

```text
my signature => Best regards,\nLuis
```

You can edit both in the Settings window.

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
- applied commands and formatter behavior

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

TypeFlow is currently an MVP focused on reliable dictation, insertion, and local-first workflow on Windows.

## Branding Assets

The repository now includes generated branding assets for the app window, tray icon, and Windows executable:

- `assets/typeflow-icon.png`
- `assets/typeflow-tray.png`
- `assets/typeflow.ico`

You can regenerate them at any time with:

```powershell
python .\scripts\generate_assets.py
```

## Windows Build

TypeFlow now includes a first `.exe` packaging workflow based on PyInstaller.

Build the app with:

```powershell
.\build.ps1
```

When the build succeeds, the executable is written to:

```text
dist\TypeFlow.exe
```

The build process currently:

- regenerates the icon assets
- packages the app as a windowed executable
- embeds the TypeFlow app icon
- includes the `assets` folder in the packaged app
