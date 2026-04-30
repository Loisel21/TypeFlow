from __future__ import annotations

import tkinter as tk
from collections.abc import Callable

from typeflow.config import AppConfig


class TypeFlowUI:
    def __init__(
        self,
        hotkey: str,
        initial_mode: str,
        on_toggle: Callable[[], None],
        on_hide: Callable[[], None],
        on_exit: Callable[[], None],
        on_open_settings: Callable[[], None],
        on_mode_change: Callable[[str], None],
    ) -> None:
        self._on_mode_change = on_mode_change
        self._root = tk.Tk()
        self._root.title("TypeFlow")
        self._root.geometry("560x360")
        self._root.resizable(False, False)
        self._root.protocol("WM_DELETE_WINDOW", on_hide)

        self._status = tk.StringVar(value="Ready")
        self._last_text = tk.StringVar(value="No transcription yet")
        self._paste_mode = tk.StringVar(value="Insert mode: Direct typing")
        self._privacy_mode = tk.StringVar(value="Privacy mode: Local only")
        self._translation_mode = tk.StringVar(value="Translation: Off")
        self._mode_var = tk.StringVar(value=initial_mode)
        self._hotkey_var = tk.StringVar(value=f"Global hotkey: {hotkey}")
        self._settings_window: tk.Toplevel | None = None

        container = tk.Frame(self._root, padx=18, pady=18)
        container.pack(fill="both", expand=True)

        tk.Label(container, text="TypeFlow", font=("Segoe UI", 18, "bold")).pack(anchor="w")
        tk.Label(
            container,
            textvariable=self._hotkey_var,
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(6, 10))
        tk.Label(
            container,
            text="Voicely-style workflow: keep the app in the background, stay in the target text field, and use the hotkey.",
            wraplength=510,
            justify="left",
            font=("Segoe UI", 9),
        ).pack(anchor="w", pady=(0, 14))

        mode_row = tk.Frame(container)
        mode_row.pack(anchor="w", pady=(0, 12))
        tk.Label(mode_row, text="Mode", font=("Segoe UI", 10, "bold")).pack(side="left")
        mode_menu = tk.OptionMenu(
            mode_row,
            self._mode_var,
            "normal",
            "email",
            "chat",
            "code",
            command=self._handle_mode_change,
        )
        mode_menu.config(width=12, font=("Segoe UI", 9))
        mode_menu.pack(side="left", padx=(12, 0))

        tk.Label(container, textvariable=self._status, font=("Segoe UI", 12, "bold")).pack(anchor="w")
        tk.Label(
            container,
            textvariable=self._last_text,
            wraplength=510,
            justify="left",
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(10, 14))
        tk.Label(container, textvariable=self._paste_mode, font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 6))
        tk.Label(container, textvariable=self._privacy_mode, font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 6))
        tk.Label(container, textvariable=self._translation_mode, font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 6))
        tk.Label(
            container,
            text="Spoken commands supported right now: Punkt, Komma, Fragezeichen, Ausrufezeichen, Doppelpunkt, Semikolon, neue Zeile, neuer Absatz, Tab, plus English equivalents.",
            wraplength=510,
            justify="left",
            font=("Segoe UI", 9),
        ).pack(anchor="w", pady=(0, 16))

        button_row = tk.Frame(container)
        button_row.pack(anchor="w")

        tk.Button(
            button_row,
            text="Start / stop recording",
            command=on_toggle,
            font=("Segoe UI", 10),
            padx=12,
            pady=6,
        ).pack(side="left")
        tk.Button(
            button_row,
            text="Settings",
            command=on_open_settings,
            font=("Segoe UI", 10),
            padx=12,
            pady=6,
        ).pack(side="left", padx=(10, 0))
        tk.Button(
            button_row,
            text="Send to background",
            command=on_hide,
            font=("Segoe UI", 10),
            padx=12,
            pady=6,
        ).pack(side="left", padx=(10, 0))
        tk.Button(
            button_row,
            text="Exit",
            command=on_exit,
            font=("Segoe UI", 10),
            padx=12,
            pady=6,
        ).pack(side="left", padx=(10, 0))

    def set_status(self, text: str) -> None:
        self._status.set(text)
        self._root.update_idletasks()

    def set_transcript(self, text: str) -> None:
        self._last_text.set(text or "No speech detected")
        self._root.update_idletasks()

    def after(self, delay_ms: int, callback: Callable[[], None]) -> None:
        self._root.after(delay_ms, callback)

    def set_paste_mode(self, paste_mode: str) -> None:
        label = "Clipboard" if paste_mode == "clipboard" else "Direct typing"
        self._paste_mode.set(f"Insert mode: {label}")
        self._root.update_idletasks()

    def set_output_mode(self, output_mode: str) -> None:
        self._mode_var.set(output_mode)
        self._root.update_idletasks()

    def set_privacy_mode(self, privacy_mode: bool) -> None:
        label = "Local only" if privacy_mode else "Cloud-ready workflow"
        self._privacy_mode.set(f"Privacy mode: {label}")
        self._root.update_idletasks()

    def set_translation_mode(self, translation_mode: str) -> None:
        labels = {
            "off": "Off",
            "de_to_en": "German -> English",
            "en_to_de": "English -> German",
        }
        self._translation_mode.set(f"Translation: {labels.get(translation_mode, 'Off')}")
        self._root.update_idletasks()

    def set_hotkey(self, hotkey: str) -> None:
        self._hotkey_var.set(f"Global hotkey: {hotkey}")
        self._root.update_idletasks()

    def show(self) -> None:
        self._root.after(0, self._show_now)

    def hide(self) -> None:
        self._root.after(0, self._hide_now)

    def run(self) -> None:
        self._root.mainloop()

    def close(self) -> None:
        if self._settings_window is not None and self._settings_window.winfo_exists():
            self._settings_window.destroy()
        self._root.destroy()

    def open_settings(self, config: AppConfig, on_save: Callable[[AppConfig], None]) -> None:
        if self._settings_window is not None and self._settings_window.winfo_exists():
            self._settings_window.lift()
            self._settings_window.focus_force()
            return

        window = tk.Toplevel(self._root)
        window.title("TypeFlow Settings")
        window.geometry("660x680")
        window.resizable(False, False)
        window.transient(self._root)
        window.grab_set()
        self._settings_window = window

        hotkey_var = tk.StringVar(value=config.hotkey)
        language_var = tk.StringVar(value=config.language)
        paste_mode_var = tk.StringVar(value=config.paste_mode)
        translation_mode_var = tk.StringVar(value=config.translation_mode)
        start_minimized_var = tk.BooleanVar(value=config.start_minimized)
        privacy_mode_var = tk.BooleanVar(value=config.privacy_mode)
        remove_fillers_var = tk.BooleanVar(value=config.remove_fillers)
        auto_stop_enabled_var = tk.BooleanVar(value=config.auto_stop_enabled)
        silence_timeout_var = tk.StringVar(value=str(config.silence_timeout_seconds))
        max_recording_var = tk.StringVar(value=str(config.max_recording_seconds))

        content = tk.Frame(window, padx=18, pady=18)
        content.pack(fill="both", expand=True)

        self._add_labeled_entry(content, "Hotkey", hotkey_var)
        self._add_labeled_menu(content, "Language", language_var, ("de", "en"))
        self._add_labeled_menu(content, "Insert mode", paste_mode_var, ("typing", "clipboard"))
        self._add_labeled_menu(content, "Translation", translation_mode_var, ("off", "de_to_en", "en_to_de"))

        toggle_row = tk.Frame(content)
        toggle_row.pack(fill="x", pady=(12, 0))
        tk.Checkbutton(
            toggle_row,
            text="Start minimized in the background",
            variable=start_minimized_var,
            font=("Segoe UI", 9),
        ).pack(anchor="w")
        tk.Checkbutton(
            toggle_row,
            text="Privacy mode: keep the workflow local-first",
            variable=privacy_mode_var,
            font=("Segoe UI", 9),
        ).pack(anchor="w")
        tk.Checkbutton(
            toggle_row,
            text="Remove filler words automatically",
            variable=remove_fillers_var,
            font=("Segoe UI", 9),
        ).pack(anchor="w")
        tk.Checkbutton(
            toggle_row,
            text="Stop recording automatically after silence",
            variable=auto_stop_enabled_var,
            font=("Segoe UI", 9),
        ).pack(anchor="w")

        self._add_labeled_entry(content, "Silence timeout (s)", silence_timeout_var)
        self._add_labeled_entry(content, "Max recording (s)", max_recording_var)

        replacements_var = tk.Text(content, height=8, width=70, font=("Consolas", 9))
        replacements_var.insert("1.0", self._format_mapping(config.custom_replacements))
        self._add_labeled_text(
            content,
            "Lexicon replacements",
            "Use one line per replacement: spoken phrase => written phrase",
            replacements_var,
        )

        snippets_var = tk.Text(content, height=8, width=70, font=("Consolas", 9))
        snippets_var.insert("1.0", self._format_mapping(config.snippets))
        self._add_labeled_text(
            content,
            "Snippets",
            "Use one line per snippet: spoken trigger => inserted text",
            snippets_var,
        )

        info = (
            "This makes TypeFlow feel closer to Voicely: personal replacements, snippets, "
            "local privacy mode, and automatic cleanup can all be tuned here."
        )
        tk.Label(content, text=info, wraplength=360, justify="left", font=("Segoe UI", 9)).pack(
            anchor="w",
            pady=(18, 18),
        )

        button_row = tk.Frame(content)
        button_row.pack(anchor="e")

        def save_settings() -> None:
            updated_config = AppConfig(
                hotkey=hotkey_var.get().strip() or config.hotkey,
                sample_rate=config.sample_rate,
                channels=config.channels,
                whisper_model=config.whisper_model,
                language=language_var.get(),
                device=config.device,
                compute_type=config.compute_type,
                beam_size=config.beam_size,
                paste_mode=paste_mode_var.get(),
                output_mode=config.output_mode,
                translation_mode=translation_mode_var.get(),
                start_minimized=start_minimized_var.get(),
                privacy_mode=privacy_mode_var.get(),
                remove_fillers=remove_fillers_var.get(),
                auto_stop_enabled=auto_stop_enabled_var.get(),
                silence_timeout_seconds=self._parse_float(silence_timeout_var.get(), config.silence_timeout_seconds),
                max_recording_seconds=self._parse_float(max_recording_var.get(), config.max_recording_seconds),
                voice_activity_threshold=config.voice_activity_threshold,
                custom_replacements=self._parse_mapping(replacements_var.get("1.0", "end")),
                snippets=self._parse_mapping(snippets_var.get("1.0", "end")),
            )
            on_save(updated_config)
            window.destroy()

        tk.Button(button_row, text="Cancel", command=window.destroy, font=("Segoe UI", 9), padx=12, pady=5).pack(
            side="left"
        )
        tk.Button(button_row, text="Save", command=save_settings, font=("Segoe UI", 9), padx=12, pady=5).pack(
            side="left",
            padx=(10, 0),
        )

    def _show_now(self) -> None:
        self._root.deiconify()
        self._root.lift()
        self._root.focus_force()

    def _hide_now(self) -> None:
        self._root.withdraw()

    def _handle_mode_change(self, value: str) -> None:
        self._on_mode_change(value)

    def _add_labeled_entry(self, parent: tk.Widget, label: str, variable: tk.StringVar) -> None:
        row = tk.Frame(parent)
        row.pack(fill="x", pady=(0, 12))
        tk.Label(row, text=label, width=14, anchor="w", font=("Segoe UI", 9, "bold")).pack(side="left")
        tk.Entry(row, textvariable=variable, font=("Segoe UI", 9), width=28).pack(side="left", fill="x", expand=True)

    def _add_labeled_menu(
        self,
        parent: tk.Widget,
        label: str,
        variable: tk.StringVar,
        values: tuple[str, ...],
    ) -> None:
        row = tk.Frame(parent)
        row.pack(fill="x", pady=(0, 12))
        tk.Label(row, text=label, width=14, anchor="w", font=("Segoe UI", 9, "bold")).pack(side="left")
        menu = tk.OptionMenu(row, variable, *values)
        menu.config(width=22, font=("Segoe UI", 9))
        menu.pack(side="left")

    def _add_labeled_text(self, parent: tk.Widget, label: str, helper: str, widget: tk.Text) -> None:
        frame = tk.Frame(parent)
        frame.pack(fill="x", pady=(14, 0))
        tk.Label(frame, text=label, anchor="w", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(frame, text=helper, anchor="w", justify="left", font=("Segoe UI", 8)).pack(anchor="w", pady=(2, 6))
        widget.pack(in_=frame, fill="x")

    def _parse_mapping(self, raw_text: str) -> dict[str, str]:
        mapping: dict[str, str] = {}
        for raw_line in raw_text.splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if "=>" not in line:
                continue
            spoken, written = line.split("=>", 1)
            spoken = spoken.strip()
            written = written.strip().replace("\\n", "\n").replace("\\t", "\t")
            if spoken and written:
                mapping[spoken] = written
        return mapping

    def _format_mapping(self, mapping: dict[str, str]) -> str:
        if not mapping:
            return ""
        return "\n".join(
            f"{spoken} => {written.replace(chr(10), '\\n').replace(chr(9), '\\t')}"
            for spoken, written in mapping.items()
        )

    def _parse_float(self, raw_value: str, fallback: float) -> float:
        try:
            value = float(raw_value.strip())
            return value if value > 0 else fallback
        except ValueError:
            return fallback
