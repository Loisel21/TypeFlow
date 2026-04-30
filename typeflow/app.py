from __future__ import annotations

import os
import threading
import traceback
from pathlib import Path
from queue import Empty, Queue

import sounddevice as sd

from typeflow.assets import asset_path, project_root
from typeflow.config import AppConfig
from typeflow.formatter import OutputFormatter
from typeflow.hotkey import GlobalHotkey
from typeflow.inserter import TextInserter
from typeflow.logger import setup_logger
from typeflow.recorder import AudioRecorder
from typeflow.tray import TypeFlowTray
from typeflow.transcriber import WhisperTranscriber
from typeflow.translator import TextTranslator
from typeflow.ui import TypeFlowUI


class TypeFlowApp:
    def __init__(self) -> None:
        self.config = AppConfig.load()
        self.logger = setup_logger()
        self.formatter = OutputFormatter()
        self.translator = TextTranslator()
        self.recorder = AudioRecorder(
            sample_rate=self.config.sample_rate,
            channels=self.config.channels,
            voice_activity_threshold=self.config.voice_activity_threshold,
        )
        self.transcriber = WhisperTranscriber(
            model_name=self.config.whisper_model,
            language=self.config.language,
            device=self.config.device,
            compute_type=self.config.compute_type,
            beam_size=self.config.beam_size,
        )
        self.inserter = TextInserter(logger=self.logger, paste_mode=self.config.paste_mode)
        self.ui = TypeFlowUI(
            hotkey=self.config.hotkey,
            initial_mode=self.config.output_mode,
            initial_translation_mode=self.config.translation_mode,
            initial_privacy_mode=self.config.privacy_mode,
            on_toggle=self.toggle_recording,
            on_hide=self.hide_to_tray,
            on_exit=self.shutdown,
            on_open_settings=self.open_settings,
            on_open_logs=self.open_logs,
            on_run_self_check=self.run_self_check,
            on_mode_change=self.set_output_mode,
            on_translation_change=self.set_translation_mode,
            on_privacy_toggle=self.set_privacy_mode,
        )
        self.tray = TypeFlowTray(
            on_show=self.show_window,
            on_hide=self.hide_to_tray,
            on_exit=self.shutdown,
        )
        self.hotkey = GlobalHotkey(self.config.hotkey, self.toggle_recording)
        self._events: Queue[tuple[str, str]] = Queue()
        self._is_processing = False
        self._is_shutting_down = False
        self._target_window: int | None = None
        self._auto_stop_after_id: str | None = None

    def run(self) -> None:
        self.tray.start()
        self.hotkey.start()
        self.ui.set_status("Ready. Press the hotkey to start dictation.")
        self.ui.set_paste_mode(self.inserter.paste_mode)
        self.ui.set_output_mode(self.config.output_mode)
        self.ui.set_translation_mode(self.config.translation_mode)
        self.ui.set_hotkey(self.config.hotkey)
        self.ui.set_privacy_mode(self.config.privacy_mode)
        self.ui.set_diagnostics("Diagnostics: click 'Run self-check' for microphone, assets, and build status.")
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
            self._events.put(("status", "Transcribing... The model may need a moment to load the first time."))
            threading.Thread(target=self._process_audio, args=(audio,), daemon=True).start()
            return

        self._target_window = self.inserter.get_active_window()
        self.logger.info("Recording started. target_window=%s", self._target_window)
        self.recorder.start()
        self._events.put(("status", "Recording..."))
        self._schedule_auto_stop_check()

    def shutdown(self) -> None:
        if self._is_shutting_down:
            return
        self._is_shutting_down = True
        self.logger.info("TypeFlow is shutting down.")
        self.hotkey.stop()
        self.tray.stop()
        if self.recorder.is_recording:
            self.recorder.stop()
        self.ui.close()

    def hide_to_tray(self) -> None:
        self.logger.info("Window sent to background.")
        self.ui.hide()
        self.tray.notify("TypeFlow", "Still running in the background.")

    def show_window(self) -> None:
        self.logger.info("Window shown again.")
        self.ui.show()

    def open_settings(self) -> None:
        self.ui.open_settings(self.config, self.apply_settings)

    def open_logs(self) -> None:
        log_file = project_root() / "logs" / "typeflow.log"
        if log_file.exists():
            os.startfile(log_file)  # type: ignore[attr-defined]
            self.ui.set_status("Log file opened")
            return

        log_dir = project_root() / "logs"
        log_dir.mkdir(exist_ok=True)
        os.startfile(log_dir)  # type: ignore[attr-defined]
        self.ui.set_status("Logs folder opened")

    def run_self_check(self) -> None:
        self.ui.set_diagnostics("Diagnostics: running self-check...")
        threading.Thread(target=self._run_self_check_worker, daemon=True).start()

    def apply_settings(self, new_config: AppConfig) -> None:
        old_hotkey = self.config.hotkey
        self.config = new_config
        self.config.save()

        self.inserter.set_paste_mode(self.config.paste_mode)
        self.transcriber.language = self.config.language
        self.recorder.voice_activity_threshold = self.config.voice_activity_threshold
        self.ui.set_paste_mode(self.config.paste_mode)
        self.ui.set_hotkey(self.config.hotkey)
        self.ui.set_privacy_mode(self.config.privacy_mode)
        self.ui.set_translation_mode(self.config.translation_mode)

        if self.config.hotkey != old_hotkey:
            self.hotkey.stop()
            self.hotkey = GlobalHotkey(self.config.hotkey, self.toggle_recording)
            self.hotkey.start()
            self.logger.info("Hotkey updated: %s", self.config.hotkey)

        self.logger.info(
            "Settings saved. hotkey=%s language=%s paste_mode=%s output_mode=%s translation_mode=%s start_minimized=%s privacy_mode=%s remove_fillers=%s auto_stop_enabled=%s silence_timeout=%s max_recording=%s replacements=%s snippets=%s",
            self.config.hotkey,
            self.config.language,
            self.config.paste_mode,
            self.config.output_mode,
            self.config.translation_mode,
            self.config.start_minimized,
            self.config.privacy_mode,
            self.config.remove_fillers,
            self.config.auto_stop_enabled,
            self.config.silence_timeout_seconds,
            self.config.max_recording_seconds,
            len(self.config.custom_replacements),
            len(self.config.snippets),
        )
        self.ui.set_status("Settings saved")

    def set_output_mode(self, output_mode: str) -> None:
        self.config.output_mode = output_mode
        self.config.save()
        self.ui.set_output_mode(output_mode)
        self.logger.info("Output mode updated: %s", output_mode)
        self.ui.set_status(f"Mode active: {output_mode}")

    def set_translation_mode(self, translation_mode: str) -> None:
        self.config.translation_mode = translation_mode
        self.config.save()
        self.ui.set_translation_mode(translation_mode)
        self.logger.info("Translation mode updated: %s", translation_mode)
        self.ui.set_status(f"Translation active: {translation_mode}")

    def set_privacy_mode(self, privacy_mode: bool) -> None:
        self.config.privacy_mode = privacy_mode
        self.config.save()
        self.ui.set_privacy_mode(privacy_mode)
        self.logger.info("Privacy mode updated: %s", privacy_mode)
        mode_label = "local only" if privacy_mode else "cloud-ready workflow"
        self.ui.set_status(f"Privacy mode active: {mode_label}")

    def _process_audio(self, audio) -> None:  # noqa: ANN001
        try:
            result = self.transcriber.transcribe(audio)
            formatted = self.formatter.format(
                result.text,
                self.config.output_mode,
                remove_fillers=self.config.remove_fillers,
                replacements=self.config.custom_replacements,
                snippets=self.config.snippets,
            )
            translated = self.translator.translate(formatted.text, self.config.translation_mode)
            final_text = translated.text
            self._events.put(("transcript", final_text or "No speech detected"))
            if result.text:
                insert_result = self.inserter.insert(final_text, target_window=self._target_window)
                if insert_result.ok:
                    status = f"Text inserted ({insert_result.method}, {self.config.output_mode}, {self.config.translation_mode})"
                    self._events.put(("status", status))
                    self.logger.info(
                        "Text inserted successfully via %s. mode=%s translation=%s commands=%s",
                        insert_result.method,
                        self.config.output_mode,
                        self.config.translation_mode,
                        ",".join(formatted.applied_commands) or "-",
                    )
                else:
                    self._events.put(("status", f"Insertion failed: {insert_result.detail}"))
                    self.logger.warning("Insertion failed: %s", insert_result.detail)
            else:
                self._events.put(("status", "No speech detected"))
        except Exception as exc:  # noqa: BLE001
            console_trace = traceback.format_exc()
            print("\n[TypeFlow] Error while processing audio:")
            print(console_trace, flush=True)
            self.logger.exception("Error while processing audio: %s", exc)
            message = f"Error: {exc}"
            self._events.put(("status", message))
            self._events.put(("transcript", str(exc)))
        finally:
            self._auto_stop_after_id = None
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
                elif event == "diagnostics":
                    self.ui.set_diagnostics(payload)
        except Empty:
            pass

        if not self._is_shutting_down:
            self.ui.after(100, self._drain_events)

    def _schedule_auto_stop_check(self) -> None:
        self.ui.after(250, self._check_auto_stop)

    def _check_auto_stop(self) -> None:
        if not self.recorder.is_recording or self._is_processing or self._is_shutting_down:
            return

        if not self.config.auto_stop_enabled:
            self._schedule_auto_stop_check()
            return

        recording_elapsed = self.recorder.recording_elapsed()
        silence_elapsed = self.recorder.silence_elapsed()

        if recording_elapsed >= self.config.max_recording_seconds:
            self.logger.info("Auto-stop triggered by max recording time: %.2fs", recording_elapsed)
            self._events.put(("status", "Stopped automatically after maximum recording time."))
            self.toggle_recording()
            return

        if self.recorder.has_detected_speech and silence_elapsed >= self.config.silence_timeout_seconds:
            self.logger.info("Auto-stop triggered by silence timeout: %.2fs", silence_elapsed)
            self._events.put(("status", "Stopped automatically after silence."))
            self.toggle_recording()
            return

        self._schedule_auto_stop_check()

    def _run_self_check_worker(self) -> None:
        checks: list[str] = []

        try:
            default_input = sd.default.device[0]
            devices = sd.query_devices()
            input_devices = [device for device in devices if int(device.get("max_input_channels", 0)) > 0]
            if default_input is not None and default_input >= 0:
                default_name = devices[int(default_input)]["name"]
                checks.append(f"Microphone OK ({default_name})")
            elif input_devices:
                checks.append(f"Microphone available ({input_devices[0]['name']})")
            else:
                checks.append("Microphone missing")
        except Exception as exc:  # noqa: BLE001
            checks.append(f"Microphone check failed ({exc})")

        try:
            import faster_whisper

            fw_root = Path(faster_whisper.__file__).resolve().parent
            vad_files = [
                fw_root / "assets" / "silero_encoder_v5.onnx",
                fw_root / "assets" / "silero_decoder_v5.onnx",
            ]
            missing_vad = [path.name for path in vad_files if not path.exists()]
            if missing_vad:
                checks.append(f"Whisper VAD assets missing ({', '.join(missing_vad)})")
            else:
                checks.append("Whisper VAD assets OK")
        except Exception as exc:  # noqa: BLE001
            checks.append(f"Whisper asset check failed ({exc})")

        icon_files = ["typeflow-icon.png", "typeflow-tray.png", "typeflow.ico"]
        missing_icons = [name for name in icon_files if not asset_path(name).exists()]
        if missing_icons:
            checks.append(f"Branding assets missing ({', '.join(missing_icons)})")
        else:
            checks.append("Branding assets OK")

        if getattr(os, "startfile", None) is None:
            checks.append("Log opening unavailable")
        else:
            checks.append("Log opening available")

        dist_exe = project_root() / "dist" / "TypeFlow.exe"
        if dist_exe.exists():
            checks.append("Windows build found")
        else:
            checks.append("Windows build missing")

        summary = "Diagnostics: " + " | ".join(checks)
        self.logger.info("Self-check completed: %s", summary)
        self._events.put(("diagnostics", summary))
        self._events.put(("status", "Self-check completed"))
