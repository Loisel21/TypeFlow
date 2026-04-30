from __future__ import annotations

import ctypes
import time
from dataclasses import dataclass
import logging

import keyboard
import pyperclip


@dataclass(slots=True)
class InsertResult:
    ok: bool
    method: str
    detail: str


class TextInserter:
    def __init__(self, logger: logging.Logger, paste_mode: str = "clipboard") -> None:
        self._user32 = ctypes.windll.user32
        self._logger = logger
        self._paste_mode = paste_mode

    def get_active_window(self) -> int | None:
        hwnd = self._user32.GetForegroundWindow()
        return int(hwnd) if hwnd else None

    def insert(self, text: str, target_window: int | None = None) -> InsertResult:
        if not text:
            return InsertResult(ok=False, method="none", detail="Kein Text zum Einfuegen")

        previous_clipboard = self._safe_paste()
        try:
            if target_window:
                self._focus_window(target_window)
            time.sleep(0.2)
            self._release_modifier_keys()
            active_window = self.get_active_window()
            self._logger.info(
                "Einfuegen gestartet. target_window=%s active_window=%s mode=%s",
                target_window,
                active_window,
                self._paste_mode,
            )

            if self._paste_mode == "typing":
                self._type_text(text)
                method = "typing"
            elif self._paste_mode == "clipboard":
                self._paste_clipboard(text)
                method = "clipboard"
            else:
                self._paste_clipboard(text)
                method = "clipboard"
            time.sleep(0.35)
            return InsertResult(ok=True, method=method, detail="Text gesendet")
        except Exception as exc:  # noqa: BLE001
            self._logger.exception("Einfuegen fehlgeschlagen: %s", exc)
            return InsertResult(ok=False, method=self._paste_mode, detail=str(exc))
        finally:
            if previous_clipboard is not None:
                time.sleep(0.35)
                pyperclip.copy(previous_clipboard)

    def _safe_paste(self) -> str | None:
        try:
            return pyperclip.paste()
        except pyperclip.PyperclipException:
            return None

    def _focus_window(self, hwnd: int) -> None:
        if not self._user32.IsWindow(hwnd):
            return

        if self._user32.IsIconic(hwnd):
            self._user32.ShowWindow(hwnd, 9)

        self._user32.SetForegroundWindow(hwnd)
        self._user32.BringWindowToTop(hwnd)
        self._user32.SetFocus(hwnd)

    @property
    def paste_mode(self) -> str:
        return self._paste_mode

    def set_paste_mode(self, paste_mode: str) -> None:
        self._paste_mode = paste_mode
        self._logger.info("Einfuegemodus aktualisiert: %s", paste_mode)

    def _paste_clipboard(self, text: str) -> None:
        pyperclip.copy(text)
        time.sleep(0.1)
        keyboard.press_and_release("ctrl+v")

    def _type_text(self, text: str) -> None:
        keyboard.write(text, delay=0.01)

    def _release_modifier_keys(self) -> None:
        for key in ("ctrl", "shift", "alt", "left windows", "right windows"):
            try:
                keyboard.release(key)
            except Exception:  # noqa: BLE001
                continue
