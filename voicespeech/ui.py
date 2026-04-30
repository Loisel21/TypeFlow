from __future__ import annotations

import tkinter as tk
from collections.abc import Callable

from voicespeech.config import AppConfig


class VoiceSpeechUI:
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
        self._root.title("VoiceSpeech")
        self._root.geometry("560x360")
        self._root.resizable(False, False)
        self._root.protocol("WM_DELETE_WINDOW", on_hide)

        self._status = tk.StringVar(value="Bereit")
        self._last_text = tk.StringVar(value="Noch keine Transkription")
        self._paste_mode = tk.StringVar(value="Einfuegemodus: Direktes Tippen")
        self._mode_var = tk.StringVar(value=initial_mode)
        self._hotkey_var = tk.StringVar(value=f"Globaler Hotkey: {hotkey}")
        self._settings_window: tk.Toplevel | None = None

        container = tk.Frame(self._root, padx=18, pady=18)
        container.pack(fill="both", expand=True)

        tk.Label(container, text="VoiceSpeech", font=("Segoe UI", 18, "bold")).pack(anchor="w")
        tk.Label(
            container,
            textvariable=self._hotkey_var,
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(6, 10))
        tk.Label(
            container,
            text="Voicely-Style Workflow: App im Hintergrund lassen, im Ziel-Textfeld bleiben, Hotkey nutzen.",
            wraplength=510,
            justify="left",
            font=("Segoe UI", 9),
        ).pack(anchor="w", pady=(0, 14))

        mode_row = tk.Frame(container)
        mode_row.pack(anchor="w", pady=(0, 12))
        tk.Label(mode_row, text="Modus", font=("Segoe UI", 10, "bold")).pack(side="left")
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
        tk.Label(
            container,
            text="Sprachbefehle: Punkt, Komma, Fragezeichen, Ausrufezeichen, Doppelpunkt, Semikolon, neue Zeile, neuer Absatz, Tab",
            wraplength=510,
            justify="left",
            font=("Segoe UI", 9),
        ).pack(anchor="w", pady=(0, 16))

        button_row = tk.Frame(container)
        button_row.pack(anchor="w")

        tk.Button(
            button_row,
            text="Aufnahme starten / stoppen",
            command=on_toggle,
            font=("Segoe UI", 10),
            padx=12,
            pady=6,
        ).pack(side="left")
        tk.Button(
            button_row,
            text="Einstellungen",
            command=on_open_settings,
            font=("Segoe UI", 10),
            padx=12,
            pady=6,
        ).pack(side="left", padx=(10, 0))
        tk.Button(
            button_row,
            text="In den Hintergrund",
            command=on_hide,
            font=("Segoe UI", 10),
            padx=12,
            pady=6,
        ).pack(side="left", padx=(10, 0))
        tk.Button(
            button_row,
            text="Beenden",
            command=on_exit,
            font=("Segoe UI", 10),
            padx=12,
            pady=6,
        ).pack(side="left", padx=(10, 0))

    def set_status(self, text: str) -> None:
        self._status.set(text)
        self._root.update_idletasks()

    def set_transcript(self, text: str) -> None:
        self._last_text.set(text or "Keine Sprache erkannt")
        self._root.update_idletasks()

    def after(self, delay_ms: int, callback: Callable[[], None]) -> None:
        self._root.after(delay_ms, callback)

    def set_paste_mode(self, paste_mode: str) -> None:
        label = "Zwischenablage" if paste_mode == "clipboard" else "Direktes Tippen"
        self._paste_mode.set(f"Einfuegemodus: {label}")
        self._root.update_idletasks()

    def set_output_mode(self, output_mode: str) -> None:
        self._mode_var.set(output_mode)
        self._root.update_idletasks()

    def set_hotkey(self, hotkey: str) -> None:
        self._hotkey_var.set(f"Globaler Hotkey: {hotkey}")
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
        window.title("VoiceSpeech Einstellungen")
        window.geometry("420x320")
        window.resizable(False, False)
        window.transient(self._root)
        window.grab_set()
        self._settings_window = window

        hotkey_var = tk.StringVar(value=config.hotkey)
        language_var = tk.StringVar(value=config.language)
        paste_mode_var = tk.StringVar(value=config.paste_mode)
        start_minimized_var = tk.BooleanVar(value=config.start_minimized)

        content = tk.Frame(window, padx=18, pady=18)
        content.pack(fill="both", expand=True)

        self._add_labeled_entry(content, "Hotkey", hotkey_var)
        self._add_labeled_menu(content, "Sprache", language_var, ("de", "en"))
        self._add_labeled_menu(content, "Einfuegemodus", paste_mode_var, ("typing", "clipboard"))

        toggle_row = tk.Frame(content)
        toggle_row.pack(fill="x", pady=(12, 0))
        tk.Checkbutton(
            toggle_row,
            text="Beim Start minimiert in den Hintergrund gehen",
            variable=start_minimized_var,
            font=("Segoe UI", 9),
        ).pack(anchor="w")

        info = (
            "Hinweis: Bei Hotkey-Aenderungen wird die globale Registrierung sofort aktualisiert. "
            "Sprachmodus waehlst du weiter direkt im Hauptfenster."
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
                start_minimized=start_minimized_var.get(),
            )
            on_save(updated_config)
            window.destroy()

        tk.Button(button_row, text="Abbrechen", command=window.destroy, font=("Segoe UI", 9), padx=12, pady=5).pack(
            side="left"
        )
        tk.Button(button_row, text="Speichern", command=save_settings, font=("Segoe UI", 9), padx=12, pady=5).pack(
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
