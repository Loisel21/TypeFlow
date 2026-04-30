from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from collections.abc import Callable

from typeflow.assets import asset_path
from typeflow.config import AppConfig


class TypeFlowUI:
    def __init__(
        self,
        hotkey: str,
        initial_mode: str,
        initial_translation_mode: str,
        initial_privacy_mode: bool,
        on_toggle: Callable[[], None],
        on_hide: Callable[[], None],
        on_exit: Callable[[], None],
        on_open_settings: Callable[[], None],
        on_open_logs: Callable[[], None],
        on_run_self_check: Callable[[], None],
        on_mode_change: Callable[[str], None],
        on_translation_change: Callable[[str], None],
        on_privacy_toggle: Callable[[bool], None],
    ) -> None:
        self._on_mode_change = on_mode_change
        self._on_translation_change = on_translation_change
        self._on_privacy_toggle = on_privacy_toggle
        self._on_open_logs = on_open_logs
        self._on_run_self_check = on_run_self_check
        self._root = tk.Tk()
        self._root.title("TypeFlow")
        self._root.geometry("520x510")
        self._root.resizable(False, False)
        self._root.protocol("WM_DELETE_WINDOW", on_hide)
        self._root.minsize(520, 510)
        self._root.attributes("-topmost", True)
        self._root.attributes("-alpha", 0.98)
        self._icon_image: tk.PhotoImage | None = None
        self._apply_window_icon()

        menu_bar = tk.Menu(self._root)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Settings", command=on_open_settings)
        file_menu.add_command(label="Open logs", command=on_open_logs)
        file_menu.add_command(label="Run self-check", command=on_run_self_check)
        file_menu.add_separator()
        file_menu.add_command(label="Send to background", command=on_hide)
        file_menu.add_command(label="Exit", command=on_exit)
        menu_bar.add_cascade(label="File", menu=file_menu)
        self._root.config(menu=menu_bar)
        self._root.bind_all("<Control-comma>", lambda _event: on_open_settings())

        self._status = tk.StringVar(value="Ready")
        self._last_text = tk.StringVar(value="No transcription yet")
        self._diagnostics = tk.StringVar(value="Diagnostics: not run yet")
        self._paste_mode = tk.StringVar(value="Insert mode: Direct typing")
        self._privacy_mode = tk.StringVar(value="Privacy mode: Local only")
        self._translation_mode = tk.StringVar(value="")
        self._translation_mode_key = tk.StringVar(value=initial_translation_mode)
        self._privacy_toggle_var = tk.BooleanVar(value=initial_privacy_mode)
        self._mode_var = tk.StringVar(value=initial_mode)
        self._hotkey_var = tk.StringVar(value=f"Global hotkey: {hotkey}")
        self._status_badge = tk.StringVar(value="Ready")
        self._overlay_title = tk.StringVar(value="Ready")
        self._overlay_hint = tk.StringVar(value=f"Press {hotkey} to start dictation")
        self._settings_window: tk.Toplevel | None = None
        self._pulse_after_id: str | None = None
        self._pulse_step = 0
        self._wave_after_id: str | None = None
        self._wave_phase = 0
        self._overlay_window: tk.Toplevel | None = None
        self._wave_bars: list[int] = []

        self._surface_color = "#f4f7fb"
        self._card_color = "#ffffff"
        self._text_color = "#16324f"
        self._muted_text_color = "#5e7488"
        self._accent_color = "#0d6e7c"
        self._accent_soft = "#d7eef2"
        self._success_color = "#0f766e"
        self._success_soft = "#d7f5ec"
        self._warning_color = "#9a6700"
        self._warning_soft = "#fff3c4"
        self._error_color = "#b42318"
        self._error_soft = "#fee4e2"

        style = ttk.Style(self._root)
        style.theme_use("clam")
        style.configure("TypeFlow.TNotebook", background=self._surface_color, borderwidth=0)
        style.configure(
            "TypeFlow.TNotebook.Tab",
            padding=(16, 8),
            font=("Segoe UI", 9, "bold"),
            background="#e8eef5",
            foreground=self._text_color,
        )
        style.map(
            "TypeFlow.TNotebook.Tab",
            background=[("selected", self._card_color)],
            foreground=[("selected", self._accent_color)],
        )

        container = tk.Frame(self._root, padx=20, pady=18, bg=self._surface_color)
        container.pack(fill="both", expand=True)
        self._root.configure(bg=self._surface_color)
        self._create_recording_overlay()

        content_area = tk.Frame(container, bg=self._surface_color)
        content_area.pack(fill="both", expand=True)

        hero = tk.Frame(content_area, bg=self._surface_color)
        hero.pack(fill="x")

        title_row = tk.Frame(hero, bg=self._surface_color)
        title_row.pack(fill="x")

        title_copy = tk.Frame(title_row, bg=self._surface_color)
        title_copy.pack(side="left", anchor="n")
        brand_row = tk.Frame(title_copy, bg=self._surface_color)
        brand_row.pack(anchor="w")
        tk.Label(brand_row, text="TypeFlow", font=("Segoe UI Semibold", 24), bg=self._surface_color, fg=self._text_color).pack(
            side="left"
        )
        tk.Label(
            brand_row,
            text="beta",
            font=("Segoe UI", 8, "bold"),
            padx=8,
            pady=3,
            bg="#dff6eb",
            fg="#0f766e",
        ).pack(side="left", padx=(10, 0), pady=(6, 0))
        tk.Label(
            title_copy,
            text="Speak naturally. Your text appears polished in any app.",
            font=("Segoe UI", 10),
            bg=self._surface_color,
            fg=self._muted_text_color,
        ).pack(anchor="w", pady=(4, 0))

        status_cluster = tk.Frame(title_row, bg=self._surface_color)
        status_cluster.pack(side="right", anchor="n", pady=(6, 0))
        self._status_badge_label = tk.Label(
            status_cluster,
            textvariable=self._status_badge,
            font=("Segoe UI Semibold", 9),
            padx=12,
            pady=6,
            bg=self._accent_soft,
            fg=self._accent_color,
        )
        self._status_badge_label.pack(anchor="e")

        tk.Label(
            hero,
            textvariable=self._hotkey_var,
            font=("Segoe UI", 10),
            bg=self._surface_color,
            fg="#496179",
        ).pack(anchor="w", pady=(10, 12))

        summary_row = tk.Frame(content_area, bg=self._surface_color)
        summary_row.pack(fill="x", pady=(0, 12))
        self._build_summary_card(summary_row, "Mode", self._mode_var, width=138).pack(side="left", fill="x", expand=True)
        self._build_summary_card(summary_row, "Insert", self._paste_mode, width=138).pack(side="left", fill="x", expand=True, padx=(
            10,
            10,
        ))
        self._build_summary_card(summary_row, "Translation", self._translation_mode, width=138).pack(side="left", fill="x", expand=True)

        workspace_card = tk.Frame(
            content_area,
            bg=self._card_color,
            bd=0,
            highlightthickness=1,
            highlightbackground="#d6e2ea",
            padx=18,
            pady=18,
        )
        workspace_card.pack(fill="x", pady=(0, 12))

        workspace_header = tk.Frame(workspace_card, bg=self._card_color)
        workspace_header.pack(fill="x")
        tk.Label(
            workspace_header,
            text="Dictation workspace",
            font=("Segoe UI", 13, "bold"),
            bg=self._card_color,
            fg=self._text_color,
        ).pack(side="left")
        privacy_chip = tk.Label(
            workspace_header,
            textvariable=self._privacy_mode,
            font=("Segoe UI", 8, "bold"),
            padx=10,
            pady=5,
            bg="#ebf8ff",
            fg="#155b75",
        )
        privacy_chip.pack(side="right")

        tk.Label(
            workspace_card,
            text="Stay in your target app, press the hotkey, and let TypeFlow write for you.",
            wraplength=430,
            justify="left",
            font=("Segoe UI", 9),
            bg=self._card_color,
            fg=self._muted_text_color,
        ).pack(anchor="w", pady=(10, 12))

        quick_toggle_row = tk.Frame(workspace_card, bg=self._card_color)
        quick_toggle_row.pack(fill="x")

        mode_row = tk.Frame(quick_toggle_row, bg=self._card_color)
        mode_row.pack(side="left")
        tk.Label(mode_row, text="Mode", font=("Segoe UI", 10, "bold"), bg=self._card_color, fg=self._text_color).pack(side="left")
        self._mode_menu = tk.OptionMenu(
            mode_row,
            self._mode_var,
            "normal",
            "email",
            "chat",
            "code",
            command=self._handle_mode_change,
        )
        self._mode_menu.config(
            width=12,
            font=("Segoe UI", 9),
            bg="#eef4fa",
            activebackground="#dce9f5",
            highlightthickness=0,
            relief="flat",
        )
        self._mode_menu.pack(side="left", padx=(12, 0))

        translation_row = tk.Frame(quick_toggle_row, bg=self._card_color)
        translation_row.pack(side="left", padx=(16, 0))
        tk.Label(
            translation_row,
            text="Translation",
            font=("Segoe UI", 10, "bold"),
            bg=self._card_color,
            fg=self._text_color,
        ).pack(side="left")
        self._translation_menu = tk.OptionMenu(
            translation_row,
            self._translation_mode_key,
            "off",
            "de_to_en",
            "en_to_de",
            command=self._handle_translation_change,
        )
        self._translation_menu.config(
            width=12,
            font=("Segoe UI", 9),
            bg="#eef4fa",
            activebackground="#dce9f5",
            highlightthickness=0,
            relief="flat",
        )
        self._translation_menu.pack(side="left", padx=(12, 0))

        privacy_toggle = tk.Checkbutton(
            quick_toggle_row,
            text="Privacy mode",
            variable=self._privacy_toggle_var,
            command=self._handle_privacy_toggle,
            font=("Segoe UI", 9, "bold"),
            bg=self._card_color,
            fg=self._text_color,
            activebackground=self._card_color,
            selectcolor="#e8f6f8",
            padx=8,
            pady=4,
        )
        privacy_toggle.pack(side="right")

        status_card = tk.Frame(
            content_area,
            bg=self._card_color,
            bd=0,
            highlightthickness=1,
            highlightbackground="#d6e2ea",
            padx=18,
            pady=18,
        )
        status_card.pack(fill="both", expand=True)

        tk.Label(status_card, text="Recent output", font=("Segoe UI", 10, "bold"), bg=self._card_color, fg=self._text_color).pack(
            anchor="w"
        )
        self._status_label = tk.Label(
            status_card,
            textvariable=self._status,
            font=("Segoe UI", 13, "bold"),
            bg=self._card_color,
            fg=self._success_color,
        )
        self._status_label.pack(anchor="w", pady=(6, 4))
        tk.Label(
            status_card,
            textvariable=self._last_text,
            wraplength=430,
            justify="left",
            font=("Segoe UI", 10),
            bg=self._card_color,
            fg="#203040",
        ).pack(anchor="w", pady=(10, 10))

        compact_meta = tk.Frame(status_card, bg=self._card_color)
        compact_meta.pack(fill="x")
        self._build_mini_chip(compact_meta, self._paste_mode).pack(side="left")
        self._build_mini_chip(compact_meta, self._translation_mode).pack(side="left", padx=(8, 0))
        self._build_mini_chip(compact_meta, self._privacy_mode).pack(side="left", padx=(8, 0))

        tk.Label(
            status_card,
            text="Recording opens a floating overlay with a live waveform so the main window can stay out of the way.",
            wraplength=430,
            justify="left",
            font=("Segoe UI", 8),
            bg=self._card_color,
            fg=self._muted_text_color,
        ).pack(anchor="w", pady=(12, 0))

        diagnostics_card = tk.Frame(
            content_area,
            bg=self._card_color,
            bd=0,
            highlightthickness=1,
            highlightbackground="#d6e2ea",
            padx=18,
            pady=16,
        )
        diagnostics_card.pack(fill="x", pady=(12, 0))
        tk.Label(
            diagnostics_card,
            text="Diagnostics",
            font=("Segoe UI", 10, "bold"),
            bg=self._card_color,
            fg=self._text_color,
        ).pack(anchor="w")
        tk.Label(
            diagnostics_card,
            textvariable=self._diagnostics,
            wraplength=430,
            justify="left",
            font=("Segoe UI", 9),
            bg=self._card_color,
            fg=self._muted_text_color,
        ).pack(anchor="w", pady=(8, 12))

        diagnostics_actions = tk.Frame(diagnostics_card, bg=self._card_color)
        diagnostics_actions.pack(fill="x")
        tk.Button(
            diagnostics_actions,
            text="Run self-check",
            command=on_run_self_check,
            font=("Segoe UI", 9),
            padx=12,
            pady=5,
            bg="#eef4fa",
            fg=self._text_color,
            activebackground="#dce9f5",
            relief="flat",
            bd=0,
            cursor="hand2",
        ).pack(side="left")
        tk.Button(
            diagnostics_actions,
            text="Open logs",
            command=on_open_logs,
            font=("Segoe UI", 9),
            padx=12,
            pady=5,
            bg="#eef4fa",
            fg=self._text_color,
            activebackground="#dce9f5",
            relief="flat",
            bd=0,
            cursor="hand2",
        ).pack(side="left", padx=(8, 0))

        button_row = tk.Frame(container, bg=self._surface_color)
        button_row.pack(fill="x", side="bottom", pady=(14, 0))

        self._toggle_button = tk.Button(
            button_row,
            text="Start dictation",
            command=on_toggle,
            font=("Segoe UI Semibold", 10),
            padx=16,
            pady=8,
            bg=self._accent_color,
            fg="white",
            activebackground="#095c6c",
            activeforeground="white",
            relief="flat",
            bd=0,
            cursor="hand2",
        )
        self._toggle_button.pack(side="left")
        tk.Button(
            button_row,
            text="Settings",
            command=on_open_settings,
            font=("Segoe UI", 10),
            padx=12,
            pady=6,
            bg=self._card_color,
            fg=self._text_color,
            activebackground="#edf3f8",
            relief="flat",
            bd=0,
            cursor="hand2",
        ).pack(side="left", padx=(10, 0))
        tk.Button(
            button_row,
            text="Send to background",
            command=on_hide,
            font=("Segoe UI", 10),
            padx=12,
            pady=6,
            bg=self._card_color,
            fg=self._text_color,
            activebackground="#edf3f8",
            relief="flat",
            bd=0,
            cursor="hand2",
        ).pack(side="left", padx=(10, 0))
        tk.Button(
            button_row,
            text="Exit",
            command=on_exit,
            font=("Segoe UI", 10),
            padx=12,
            pady=6,
            bg=self._card_color,
            fg=self._text_color,
            activebackground="#edf3f8",
            relief="flat",
            bd=0,
            cursor="hand2",
        ).pack(side="right")

        self.set_status("Ready")
        self.set_translation_mode(initial_translation_mode)
        self.set_privacy_mode(initial_privacy_mode)

    def set_status(self, text: str) -> None:
        self._status.set(text)
        self._update_status_appearance(text)
        self._root.update_idletasks()

    def set_transcript(self, text: str) -> None:
        self._last_text.set(text or "No speech detected")
        self._root.update_idletasks()

    def set_diagnostics(self, text: str) -> None:
        self._diagnostics.set(text)
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
        self._privacy_toggle_var.set(privacy_mode)
        self._root.update_idletasks()

    def set_translation_mode(self, translation_mode: str) -> None:
        labels = {
            "off": "Off",
            "de_to_en": "German -> English",
            "en_to_de": "English -> German",
        }
        self._translation_mode.set(f"Translation: {labels.get(translation_mode, 'Off')}")
        self._translation_mode_key.set(translation_mode)
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
        if self._overlay_window is not None and self._overlay_window.winfo_exists():
            self._overlay_window.destroy()
        self._root.destroy()

    def open_settings(self, config: AppConfig, on_save: Callable[[AppConfig], None]) -> None:
        if self._settings_window is not None and self._settings_window.winfo_exists():
            self._settings_window.lift()
            self._settings_window.focus_force()
            return

        window = tk.Toplevel(self._root)
        window.title("TypeFlow Settings")
        self._root.update_idletasks()
        screen_width = self._root.winfo_screenwidth()
        screen_height = self._root.winfo_screenheight()
        width = min(720, max(620, screen_width - 120))
        height = min(760, max(520, screen_height - 120))
        x = max(40, (screen_width - width) // 2)
        y = max(40, (screen_height - height) // 2)
        window.geometry(f"{width}x{height}+{x}+{y}")
        window.minsize(620, 520)
        window.resizable(True, True)
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

        outer = tk.Frame(window)
        outer.pack(fill="both", expand=True)

        canvas = tk.Canvas(outer, highlightthickness=0)
        scrollbar = tk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        content = tk.Frame(canvas, padx=18, pady=18, bg="#f7f9fc")
        content_window = canvas.create_window((0, 0), window=content, anchor="nw")

        def sync_scroll_region(event) -> None:  # noqa: ANN001
            canvas.configure(scrollregion=canvas.bbox("all"))

        def sync_content_width(event) -> None:  # noqa: ANN001
            canvas.itemconfigure(content_window, width=event.width)

        content.bind("<Configure>", sync_scroll_region)
        canvas.bind("<Configure>", sync_content_width)
        canvas.bind_all(
            "<MouseWheel>",
            lambda event: canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"),
        )

        def close_settings() -> None:
            canvas.unbind_all("<MouseWheel>")
            window.destroy()

        window.protocol("WM_DELETE_WINDOW", close_settings)

        header = tk.Label(
            content,
            text="Settings",
            font=("Segoe UI", 18, "bold"),
            bg="#f7f9fc",
            fg="#16324f",
        )
        header.pack(anchor="w", pady=(0, 10))

        notebook = ttk.Notebook(content, style="TypeFlow.TNotebook")
        notebook.pack(fill="both", expand=True)

        general_tab = tk.Frame(notebook, bg="white", padx=18, pady=18)
        translation_tab = tk.Frame(notebook, bg="white", padx=18, pady=18)
        personalization_tab = tk.Frame(notebook, bg="white", padx=18, pady=18)
        recording_tab = tk.Frame(notebook, bg="white", padx=18, pady=18)

        notebook.add(general_tab, text="General")
        notebook.add(translation_tab, text="Translation")
        notebook.add(personalization_tab, text="Personalization")
        notebook.add(recording_tab, text="Recording")

        self._add_labeled_entry(general_tab, "Hotkey", hotkey_var)
        self._add_labeled_menu(general_tab, "Language", language_var, ("de", "en"))
        self._add_labeled_menu(general_tab, "Insert mode", paste_mode_var, ("typing", "clipboard"))

        general_toggle_row = tk.Frame(general_tab, bg="white")
        general_toggle_row.pack(fill="x", pady=(12, 0))
        tk.Checkbutton(
            general_toggle_row,
            text="Start minimized in the background",
            variable=start_minimized_var,
            font=("Segoe UI", 9),
            bg="white",
        ).pack(anchor="w")
        tk.Checkbutton(
            general_toggle_row,
            text="Privacy mode: keep the workflow local-first",
            variable=privacy_mode_var,
            font=("Segoe UI", 9),
            bg="white",
        ).pack(anchor="w")

        self._add_labeled_menu(translation_tab, "Translation", translation_mode_var, ("off", "de_to_en", "en_to_de"))
        tk.Label(
            translation_tab,
            text="Translation runs after formatting and before insertion. Keep it off if you want strict local-only behavior.",
            wraplength=max(420, width - 220),
            justify="left",
            font=("Segoe UI", 9),
            bg="white",
            fg="#5e7488",
        ).pack(anchor="w", pady=(12, 0))

        replacements_var = tk.Text(personalization_tab, height=8, width=70, font=("Consolas", 9))
        replacements_var.insert("1.0", self._format_mapping(config.custom_replacements))
        self._add_labeled_text(
            personalization_tab,
            "Lexicon replacements",
            "Use one line per replacement: spoken phrase => written phrase",
            replacements_var,
        )

        snippets_var = tk.Text(personalization_tab, height=8, width=70, font=("Consolas", 9))
        snippets_var.insert("1.0", self._format_mapping(config.snippets))
        self._add_labeled_text(
            personalization_tab,
            "Snippets",
            "Use one line per snippet: spoken trigger => inserted text",
            snippets_var,
        )

        recording_toggle_row = tk.Frame(recording_tab, bg="white")
        recording_toggle_row.pack(fill="x", pady=(0, 8))
        tk.Checkbutton(
            recording_toggle_row,
            text="Remove filler words automatically",
            variable=remove_fillers_var,
            font=("Segoe UI", 9),
            bg="white",
        ).pack(anchor="w")
        tk.Checkbutton(
            recording_toggle_row,
            text="Stop recording automatically after silence",
            variable=auto_stop_enabled_var,
            font=("Segoe UI", 9),
            bg="white",
        ).pack(anchor="w")

        self._add_labeled_entry(recording_tab, "Silence timeout (s)", silence_timeout_var)
        self._add_labeled_entry(recording_tab, "Max recording (s)", max_recording_var)

        info = "TypeFlow is now organized more like a product settings surface: core preferences, translation, personalization, and recording behavior are separated for faster access."
        tk.Label(content, text=info, wraplength=max(420, width - 220), justify="left", font=("Segoe UI", 9), bg="#f7f9fc", fg="#5e7488").pack(
            anchor="w",
            pady=(18, 18),
        )

        button_row = tk.Frame(content, bg="#f7f9fc")
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
            close_settings()

        tk.Button(button_row, text="Cancel", command=close_settings, font=("Segoe UI", 9), padx=12, pady=5).pack(
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

    def _handle_translation_change(self, value: str) -> None:
        self._on_translation_change(value)

    def _handle_privacy_toggle(self) -> None:
        self._on_privacy_toggle(self._privacy_toggle_var.get())

    def _apply_window_icon(self) -> None:
        icon_ico = asset_path("typeflow.ico")
        icon_png = asset_path("typeflow-icon.png")
        try:
            if icon_ico.exists():
                self._root.iconbitmap(default=str(icon_ico))
                return
        except tk.TclError:
            pass

        if icon_png.exists():
            try:
                self._icon_image = tk.PhotoImage(file=str(icon_png))
                self._root.iconphoto(True, self._icon_image)
            except tk.TclError:
                self._icon_image = None

    def _build_summary_card(self, parent: tk.Widget, title: str, variable: tk.StringVar, width: int) -> tk.Frame:
        card = tk.Frame(parent, bg=self._card_color, bd=0, highlightthickness=1, highlightbackground="#d6e2ea", padx=14, pady=12)
        card.configure(width=width)
        card.pack_propagate(False)
        tk.Label(card, text=title, font=("Segoe UI", 8, "bold"), bg=self._card_color, fg=self._muted_text_color).pack(anchor="w")
        tk.Label(card, textvariable=variable, font=("Segoe UI Semibold", 10), bg=self._card_color, fg=self._text_color, wraplength=140, justify="left").pack(
            anchor="w", pady=(8, 0)
        )
        return card

    def _build_mini_chip(self, parent: tk.Widget, variable: tk.StringVar) -> tk.Frame:
        chip = tk.Frame(parent, bg="#edf4f8", padx=10, pady=6)
        tk.Label(
            chip,
            textvariable=variable,
            font=("Segoe UI", 8, "bold"),
            bg="#edf4f8",
            fg="#33526b",
            wraplength=120,
            justify="left",
        ).pack(anchor="w")
        return chip

    def _update_status_appearance(self, text: str) -> None:
        lowered = text.lower()
        badge_text = "Ready"
        badge_fg = self._accent_color
        badge_bg = self._accent_soft
        status_fg = self._success_color
        button_text = "Start dictation"
        is_recording = False
        is_processing = False

        if "recording" in lowered:
            badge_text = "Recording"
            badge_fg = self._warning_color
            badge_bg = self._warning_soft
            status_fg = self._warning_color
            button_text = "Stop dictation"
            is_recording = True
            self._overlay_title.set("Listening...")
            self._overlay_hint.set("Speak naturally. TypeFlow is capturing your voice.")
        elif "transcrib" in lowered or "processing" in lowered:
            badge_text = "Processing"
            badge_fg = self._accent_color
            badge_bg = self._accent_soft
            status_fg = self._accent_color
            button_text = "Processing..."
            is_processing = True
            self._overlay_title.set("Processing...")
            self._overlay_hint.set("Turning your speech into polished text.")
        elif "error" in lowered or "failed" in lowered:
            badge_text = "Needs attention"
            badge_fg = self._error_color
            badge_bg = self._error_soft
            status_fg = self._error_color
            self._overlay_title.set("Something needs attention")
            self._overlay_hint.set(text)
        elif "saved" in lowered or "inserted" in lowered or "stopped automatically" in lowered:
            badge_text = "Done"
            badge_fg = self._success_color
            badge_bg = self._success_soft
            status_fg = self._success_color
            self._overlay_title.set("Done")
            self._overlay_hint.set(text)
        else:
            self._overlay_title.set("Ready")
            self._overlay_hint.set("Press the hotkey to start dictation.")

        self._status_badge.set(badge_text)
        self._status_badge_label.configure(bg=badge_bg, fg=badge_fg)
        self._status_label.configure(fg=status_fg)
        self._toggle_button.configure(text=button_text, state="disabled" if button_text == "Processing..." else "normal")
        self._set_recording_pulse(is_recording)
        self._set_overlay_state(is_recording, is_processing, badge_bg, badge_fg)

    def _set_recording_pulse(self, enabled: bool) -> None:
        if enabled:
            if self._pulse_after_id is None:
                self._pulse_step = 0
                self._run_recording_pulse()
            return

        if self._pulse_after_id is not None:
            self._root.after_cancel(self._pulse_after_id)
            self._pulse_after_id = None
        self._toggle_button.configure(bg=self._accent_color, activebackground="#095c6c")

    def _run_recording_pulse(self) -> None:
        palette = (
            (self._warning_soft, self._warning_color, "#d98804"),
            ("#ffe8a3", self._warning_color, "#b36d00"),
            ("#ffd37a", self._warning_color, "#9a6700"),
        )
        badge_bg, badge_fg, button_bg = palette[self._pulse_step % len(palette)]
        self._status_badge_label.configure(bg=badge_bg, fg=badge_fg)
        self._toggle_button.configure(bg=button_bg, activebackground=button_bg)
        self._pulse_step += 1
        self._pulse_after_id = self._root.after(220, self._run_recording_pulse)

    def _create_recording_overlay(self) -> None:
        overlay = tk.Toplevel(self._root)
        overlay.withdraw()
        overlay.overrideredirect(True)
        overlay.attributes("-topmost", True)
        overlay.configure(bg="#0f1722")
        overlay.wm_attributes("-alpha", 0.97)
        self._overlay_window = overlay

        shell = tk.Frame(overlay, bg="#0f1722", padx=18, pady=16, highlightthickness=1, highlightbackground="#1f344b")
        shell.pack(fill="both", expand=True)

        top_row = tk.Frame(shell, bg="#0f1722")
        top_row.pack(fill="x")
        self._overlay_dot = tk.Label(top_row, text="●", font=("Segoe UI", 14, "bold"), bg="#0f1722", fg="#fbbf24")
        self._overlay_dot.pack(side="left")
        tk.Label(
            top_row,
            textvariable=self._overlay_title,
            font=("Segoe UI", 13, "bold"),
            bg="#0f1722",
            fg="#f8fafc",
        ).pack(side="left", padx=(8, 0))

        self._overlay_canvas = tk.Canvas(shell, width=248, height=48, bg="#0f1722", highlightthickness=0)
        self._overlay_canvas.pack(pady=(14, 10))
        self._wave_bars.clear()
        for index in range(12):
            x0 = 10 + index * 19
            bar = self._overlay_canvas.create_rectangle(x0, 24, x0 + 10, 24, fill="#1fb6cc", width=0)
            self._wave_bars.append(bar)

        tk.Label(
            shell,
            textvariable=self._overlay_hint,
            font=("Segoe UI", 9),
            bg="#0f1722",
            fg="#c7d2de",
            wraplength=250,
            justify="left",
        ).pack(anchor="w")

    def _set_overlay_state(self, is_recording: bool, is_processing: bool, badge_bg: str, badge_fg: str) -> None:
        if self._overlay_window is None or not self._overlay_window.winfo_exists():
            return

        if is_recording or is_processing:
            self._show_overlay()
        else:
            self._hide_overlay()
            return

        self._overlay_dot.configure(fg=badge_fg)
        self._overlay_canvas.configure(bg="#0f1722")

        if is_recording:
            self._start_wave_animation()
        else:
            self._stop_wave_animation()
            for index, bar in enumerate(self._wave_bars):
                self._overlay_canvas.coords(bar, *self._wave_rect(index, 16))
                self._overlay_canvas.itemconfigure(bar, fill="#1fb6cc")

    def _show_overlay(self) -> None:
        if self._overlay_window is None or not self._overlay_window.winfo_exists():
            return
        self._overlay_window.deiconify()
        self._overlay_window.lift()
        self._position_overlay()

    def _hide_overlay(self) -> None:
        self._stop_wave_animation()
        if self._overlay_window is not None and self._overlay_window.winfo_exists():
            self._overlay_window.withdraw()

    def _position_overlay(self) -> None:
        if self._overlay_window is None or not self._overlay_window.winfo_exists():
            return
        self._root.update_idletasks()
        screen_width = self._root.winfo_screenwidth()
        screen_height = self._root.winfo_screenheight()
        width = 284
        height = 126
        x = screen_width - width - 40
        y = screen_height - height - 80
        self._overlay_window.geometry(f"{width}x{height}+{x}+{y}")

    def _start_wave_animation(self) -> None:
        if self._wave_after_id is None:
            self._wave_phase = 0
            self._animate_wave()

    def _stop_wave_animation(self) -> None:
        if self._wave_after_id is not None:
            self._root.after_cancel(self._wave_after_id)
            self._wave_after_id = None

    def _animate_wave(self) -> None:
        heights = (10, 18, 26, 34, 42, 30, 20, 38)
        for index, bar in enumerate(self._wave_bars):
            height = heights[(index + self._wave_phase) % len(heights)]
            self._overlay_canvas.coords(bar, *self._wave_rect(index, height))
            fill = "#4dd0e1" if height >= 30 else "#1fb6cc"
            self._overlay_canvas.itemconfigure(bar, fill=fill)
        self._wave_phase = (self._wave_phase + 1) % len(heights)
        self._wave_after_id = self._root.after(120, self._animate_wave)

    def _wave_rect(self, index: int, height: int) -> tuple[int, int, int, int]:
        x0 = 10 + index * 19
        center = 24
        half = height // 2
        return (x0, center - half, x0 + 10, center + half)

    def _add_labeled_entry(self, parent: tk.Widget, label: str, variable: tk.StringVar) -> None:
        row = tk.Frame(parent, bg=parent.cget("bg"))
        row.pack(fill="x", pady=(0, 12))
        tk.Label(row, text=label, width=16, anchor="w", font=("Segoe UI", 9, "bold"), bg=parent.cget("bg"), fg="#16324f").pack(side="left")
        tk.Entry(row, textvariable=variable, font=("Segoe UI", 9), width=28).pack(side="left", fill="x", expand=True)

    def _add_labeled_menu(
        self,
        parent: tk.Widget,
        label: str,
        variable: tk.StringVar,
        values: tuple[str, ...],
    ) -> None:
        row = tk.Frame(parent, bg=parent.cget("bg"))
        row.pack(fill="x", pady=(0, 12))
        tk.Label(row, text=label, width=16, anchor="w", font=("Segoe UI", 9, "bold"), bg=parent.cget("bg"), fg="#16324f").pack(side="left")
        menu = tk.OptionMenu(row, variable, *values)
        menu.config(width=22, font=("Segoe UI", 9))
        menu.pack(side="left")

    def _add_labeled_text(self, parent: tk.Widget, label: str, helper: str, widget: tk.Text) -> None:
        frame = tk.Frame(parent, bg=parent.cget("bg"))
        frame.pack(fill="x", pady=(14, 0))
        tk.Label(frame, text=label, anchor="w", font=("Segoe UI", 9, "bold"), bg=parent.cget("bg"), fg="#16324f").pack(anchor="w")
        tk.Label(frame, text=helper, anchor="w", justify="left", font=("Segoe UI", 8), bg=parent.cget("bg"), fg="#5e7488").pack(anchor="w", pady=(2, 6))
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
