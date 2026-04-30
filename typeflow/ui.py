from __future__ import annotations

import tkinter as tk
from tkinter import ttk
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
        self._root.geometry("620x420")
        self._root.resizable(False, False)
        self._root.protocol("WM_DELETE_WINDOW", on_hide)
        self._root.minsize(620, 420)

        menu_bar = tk.Menu(self._root)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Settings", command=on_open_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Send to background", command=on_hide)
        file_menu.add_command(label="Exit", command=on_exit)
        menu_bar.add_cascade(label="File", menu=file_menu)
        self._root.config(menu=menu_bar)
        self._root.bind_all("<Control-comma>", lambda _event: on_open_settings())

        self._status = tk.StringVar(value="Ready")
        self._last_text = tk.StringVar(value="No transcription yet")
        self._paste_mode = tk.StringVar(value="Insert mode: Direct typing")
        self._privacy_mode = tk.StringVar(value="Privacy mode: Local only")
        self._translation_mode = tk.StringVar(value="Translation: Off")
        self._mode_var = tk.StringVar(value=initial_mode)
        self._hotkey_var = tk.StringVar(value=f"Global hotkey: {hotkey}")
        self._status_badge = tk.StringVar(value="Ready")
        self._settings_window: tk.Toplevel | None = None

        self._surface_color = "#f4f7fb"
        self._card_color = "#ffffff"
        self._text_color = "#16324f"
        self._muted_text_color = "#5e7488"
        self._accent_color = "#0b7285"
        self._accent_soft = "#d9f0f3"
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

        content_area = tk.Frame(container, bg=self._surface_color)
        content_area.pack(fill="both", expand=True)

        hero = tk.Frame(content_area, bg=self._surface_color)
        hero.pack(fill="x")

        title_row = tk.Frame(hero, bg=self._surface_color)
        title_row.pack(fill="x")

        title_copy = tk.Frame(title_row, bg=self._surface_color)
        title_copy.pack(side="left", anchor="n")
        tk.Label(title_copy, text="TypeFlow", font=("Segoe UI", 24, "bold"), bg=self._surface_color, fg=self._text_color).pack(
            anchor="w"
        )
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
            font=("Segoe UI", 9, "bold"),
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
        ).pack(anchor="w", pady=(10, 14))

        summary_row = tk.Frame(content_area, bg=self._surface_color)
        summary_row.pack(fill="x", pady=(0, 14))
        self._build_summary_card(summary_row, "Mode", self._mode_var, width=172).pack(side="left", fill="x", expand=True)
        self._build_summary_card(summary_row, "Insert", self._paste_mode, width=172).pack(side="left", fill="x", expand=True, padx=(
            10,
            10,
        ))
        self._build_summary_card(summary_row, "Translation", self._translation_mode, width=172).pack(side="left", fill="x", expand=True)

        workspace_card = tk.Frame(
            content_area,
            bg=self._card_color,
            bd=0,
            highlightthickness=1,
            highlightbackground="#dbe3ec",
            padx=18,
            pady=18,
        )
        workspace_card.pack(fill="x", pady=(0, 14))

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
            text="Keep TypeFlow in the background, stay in your target field, press the hotkey, and let the text flow in automatically.",
            wraplength=530,
            justify="left",
            font=("Segoe UI", 9),
            bg=self._card_color,
            fg=self._muted_text_color,
        ).pack(anchor="w", pady=(10, 14))

        mode_row = tk.Frame(workspace_card, bg=self._card_color)
        mode_row.pack(fill="x")
        tk.Label(mode_row, text="Mode", font=("Segoe UI", 10, "bold"), bg=self._card_color, fg=self._text_color).pack(side="left")
        mode_menu = tk.OptionMenu(
            mode_row,
            self._mode_var,
            "normal",
            "email",
            "chat",
            "code",
            command=self._handle_mode_change,
        )
        mode_menu.config(
            width=12,
            font=("Segoe UI", 9),
            bg="#eef4fa",
            activebackground="#dce9f5",
            highlightthickness=0,
            relief="flat",
        )
        mode_menu.pack(side="left", padx=(12, 0))

        status_card = tk.Frame(
            content_area,
            bg=self._card_color,
            bd=0,
            highlightthickness=1,
            highlightbackground="#dbe3ec",
            padx=18,
            pady=18,
        )
        status_card.pack(fill="both", expand=True)

        tk.Label(status_card, text="Live status", font=("Segoe UI", 10, "bold"), bg=self._card_color, fg=self._text_color).pack(
            anchor="w"
        )
        self._status_label = tk.Label(
            status_card,
            textvariable=self._status,
            font=("Segoe UI", 15, "bold"),
            bg=self._card_color,
            fg=self._success_color,
        )
        self._status_label.pack(anchor="w", pady=(6, 4))
        tk.Label(
            status_card,
            textvariable=self._last_text,
            wraplength=510,
            justify="left",
            font=("Segoe UI", 10),
            bg=self._card_color,
            fg="#203040",
        ).pack(anchor="w", pady=(10, 12))

        workflow_strip = tk.Frame(status_card, bg=self._card_color)
        workflow_strip.pack(fill="x", pady=(2, 0))
        self._build_step_card(workflow_strip, "1", "Press hotkey", "Start dictation from any text field.").pack(
            side="left", fill="both", expand=True
        )
        self._build_step_card(workflow_strip, "2", "Speak naturally", "Filler words and pauses can be cleaned up automatically.").pack(
            side="left", fill="both", expand=True, padx=(10, 10)
        )
        self._build_step_card(workflow_strip, "3", "Text appears", "TypeFlow inserts formatted text right where you work.").pack(
            side="left", fill="both", expand=True
        )

        tk.Label(
            status_card,
            text="Supports punctuation commands in German and English, translation modes, snippets, and a local-first privacy workflow.",
            wraplength=510,
            justify="left",
            font=("Segoe UI", 9),
            bg=self._card_color,
            fg=self._muted_text_color,
        ).pack(anchor="w", pady=(14, 0))

        button_row = tk.Frame(container, bg=self._surface_color)
        button_row.pack(fill="x", side="bottom", pady=(14, 0))

        self._toggle_button = tk.Button(
            button_row,
            text="Start dictation",
            command=on_toggle,
            font=("Segoe UI", 10),
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

    def set_status(self, text: str) -> None:
        self._status.set(text)
        self._update_status_appearance(text)
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

    def _build_summary_card(self, parent: tk.Widget, title: str, variable: tk.StringVar, width: int) -> tk.Frame:
        card = tk.Frame(parent, bg=self._card_color, bd=0, highlightthickness=1, highlightbackground="#dbe3ec", padx=14, pady=12)
        card.configure(width=width)
        card.pack_propagate(False)
        tk.Label(card, text=title, font=("Segoe UI", 8, "bold"), bg=self._card_color, fg=self._muted_text_color).pack(anchor="w")
        tk.Label(card, textvariable=variable, font=("Segoe UI", 10, "bold"), bg=self._card_color, fg=self._text_color, wraplength=140, justify="left").pack(
            anchor="w", pady=(8, 0)
        )
        return card

    def _build_step_card(self, parent: tk.Widget, number: str, title: str, copy: str) -> tk.Frame:
        card = tk.Frame(parent, bg="#f8fbfd", bd=0, highlightthickness=1, highlightbackground="#e3edf5", padx=12, pady=12)
        badge = tk.Label(card, text=number, font=("Segoe UI", 8, "bold"), width=3, padx=0, pady=4, bg=self._accent_soft, fg=self._accent_color)
        badge.pack(anchor="w")
        tk.Label(card, text=title, font=("Segoe UI", 10, "bold"), bg="#f8fbfd", fg=self._text_color).pack(anchor="w", pady=(8, 4))
        tk.Label(card, text=copy, wraplength=145, justify="left", font=("Segoe UI", 8), bg="#f8fbfd", fg=self._muted_text_color).pack(anchor="w")
        return card

    def _update_status_appearance(self, text: str) -> None:
        lowered = text.lower()
        badge_text = "Ready"
        badge_fg = self._accent_color
        badge_bg = self._accent_soft
        status_fg = self._success_color
        button_text = "Start dictation"

        if "recording" in lowered:
            badge_text = "Recording"
            badge_fg = self._warning_color
            badge_bg = self._warning_soft
            status_fg = self._warning_color
            button_text = "Stop dictation"
        elif "transcrib" in lowered or "processing" in lowered:
            badge_text = "Processing"
            badge_fg = self._accent_color
            badge_bg = self._accent_soft
            status_fg = self._accent_color
            button_text = "Processing..."
        elif "error" in lowered or "failed" in lowered:
            badge_text = "Needs attention"
            badge_fg = self._error_color
            badge_bg = self._error_soft
            status_fg = self._error_color
        elif "saved" in lowered or "inserted" in lowered or "stopped automatically" in lowered:
            badge_text = "Done"
            badge_fg = self._success_color
            badge_bg = self._success_soft
            status_fg = self._success_color

        self._status_badge.set(badge_text)
        self._status_badge_label.configure(bg=badge_bg, fg=badge_fg)
        self._status_label.configure(fg=status_fg)
        self._toggle_button.configure(text=button_text, state="disabled" if button_text == "Processing..." else "normal")

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
