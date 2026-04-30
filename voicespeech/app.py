from __future__ import annotations

import threading
import traceback
from queue import Empty, Queue

from voicespeech.config import AppConfig
from voicespeech.formatter import OutputFormatter
from voicespeech.hotkey import GlobalHotkey
from voicespeech.inserter import TextInserter
from voicespeech.logger import setup_logger
from voicespeech.recorder import AudioRecorder
from voicespeech.tray import VoiceSpeechTray
from voicespeech.transcriber import WhisperTranscriber
from voicespeech.ui import VoiceSpeechUI


class VoiceSpeechApp:
    def __init__(self) -> None:
        self.config = AppConfig.load()
        self.logger = setup_logger()
        self.formatter = OutputFormatter()
        self.recorder = AudioRecorder(
            sample_rate=self.config.sample_rate,
            channels=self.config.channels,
        )
        self.transcriber = WhisperTranscriber(
            model_name=self.config.whisper_model,
            language=self.config.language,
            device=self.config.device,
            compute_type=self.config.compute_type,
            beam_size=self.config.beam_size,
        )
        self.inserter = TextInserter(logger=self.logger, paste_mode=self.config.paste_mode)
        self.ui = VoiceSpeechUI(
            hotkey=self.config.hotkey,
            initial_mode=self.config.output_mode,
            on_toggle=self.toggle_recording,
            on_hide=self.hide_to_tray,
            on_exit=self.shutdown,
            on_open_settings=self.open_settings,
            on_mode_change=self.set_output_mode,
        )
        self.tray = VoiceSpeechTray(
            on_show=self.show_window,
            on_hide=self.hide_to_tray,
            on_exit=self.shutdown,
        )
        self.hotkey = GlobalHotkey(self.config.hotkey, self.toggle_recording)
        self._events: Queue[tuple[str, str]] = Queue()
        self._is_processing = False
        self._is_shutting_down = False
        self._target_window: int | None = None

    def run(self) -> None:
        self.tray.start()
        self.hotkey.start()
        self.ui.set_status("Bereit. Hotkey druecken zum Diktieren.")
        self.ui.set_paste_mode(self.inserter.paste_mode)
        self.ui.set_output_mode(self.config.output_mode)
        self.ui.set_hotkey(self.config.hotkey)
        if self.config.start_minimized:
            self.ui.hide()
        self.ui.after(100, self._drain_events)
        self.ui.run()

    def toggle_recording(self) -> None:
        if self._is_processing:
            return

        if self.recorder.is_recording:
            audio = self.recorder.stop()
            self._is_processing = True
            self._events.put(("status", "Transkribiere... Beim ersten Mal kann das Modell kurz laden."))
            threading.Thread(target=self._process_audio, args=(audio,), daemon=True).start()
            return

        self._target_window = self.inserter.get_active_window()
        self.logger.info("Aufnahme gestartet. target_window=%s", self._target_window)
        self.recorder.start()
        self._events.put(("status", "Aufnahme laeuft..."))

    def shutdown(self) -> None:
        if self._is_shutting_down:
            return
        self._is_shutting_down = True
        self.logger.info("VoiceSpeech wird beendet.")
        self.hotkey.stop()
        self.tray.stop()
        if self.recorder.is_recording:
            self.recorder.stop()
        self.ui.close()

    def hide_to_tray(self) -> None:
        self.logger.info("Fenster in den Hintergrund gesendet.")
        self.ui.hide()
        self.tray.notify("VoiceSpeech", "Laeuft im Hintergrund weiter.")

    def show_window(self) -> None:
        self.logger.info("Fenster wieder angezeigt.")
        self.ui.show()

    def open_settings(self) -> None:
        self.ui.open_settings(self.config, self.apply_settings)

    def apply_settings(self, new_config: AppConfig) -> None:
        old_hotkey = self.config.hotkey
        self.config = new_config
        self.config.save()

        self.inserter.set_paste_mode(self.config.paste_mode)
        self.transcriber.language = self.config.language
        self.ui.set_paste_mode(self.config.paste_mode)
        self.ui.set_hotkey(self.config.hotkey)

        if self.config.hotkey != old_hotkey:
            self.hotkey.stop()
            self.hotkey = GlobalHotkey(self.config.hotkey, self.toggle_recording)
            self.hotkey.start()
            self.logger.info("Hotkey aktualisiert: %s", self.config.hotkey)

        self.logger.info(
            "Einstellungen gespeichert. hotkey=%s language=%s paste_mode=%s output_mode=%s start_minimized=%s",
            self.config.hotkey,
            self.config.language,
            self.config.paste_mode,
            self.config.output_mode,
            self.config.start_minimized,
        )
        self.ui.set_status("Einstellungen gespeichert")

    def set_output_mode(self, output_mode: str) -> None:
        self.config.output_mode = output_mode
        self.config.save()
        self.ui.set_output_mode(output_mode)
        self.logger.info("Ausgabemodus aktualisiert: %s", output_mode)
        self.ui.set_status(f"Modus aktiv: {output_mode}")

    def _process_audio(self, audio) -> None:  # noqa: ANN001
        try:
            result = self.transcriber.transcribe(audio)
            formatted = self.formatter.format(result.text, self.config.output_mode)
            self._events.put(("transcript", formatted.text or "Keine Sprache erkannt"))
            if result.text:
                insert_result = self.inserter.insert(formatted.text, target_window=self._target_window)
                if insert_result.ok:
                    status = f"Text eingefuegt ({insert_result.method}, {self.config.output_mode})"
                    self._events.put(("status", status))
                    self.logger.info(
                        "Text erfolgreich eingefuegt via %s. mode=%s commands=%s",
                        insert_result.method,
                        self.config.output_mode,
                        ",".join(formatted.applied_commands) or "-",
                    )
                else:
                    self._events.put(("status", f"Einfuegen fehlgeschlagen: {insert_result.detail}"))
                    self.logger.warning("Einfuegen fehlgeschlagen: %s", insert_result.detail)
            else:
                self._events.put(("status", "Keine Sprache erkannt"))
        except Exception as exc:  # noqa: BLE001
            console_trace = traceback.format_exc()
            print("\n[VoiceSpeech] Fehler bei der Audioverarbeitung:")
            print(console_trace, flush=True)
            self.logger.exception("Fehler bei der Audioverarbeitung: %s", exc)
            message = f"Fehler: {exc}"
            self._events.put(("status", message))
            self._events.put(("transcript", str(exc)))
        finally:
            self._target_window = None
            self._is_processing = False

    def _drain_events(self) -> None:
        try:
            while True:
                event, payload = self._events.get_nowait()
                if event == "status":
                    self.ui.set_status(payload)
                elif event == "transcript":
                    self.ui.set_transcript(payload)
        except Empty:
            pass

        if not self._is_shutting_down:
            self.ui.after(100, self._drain_events)
