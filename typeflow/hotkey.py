from collections.abc import Callable

import keyboard


class GlobalHotkey:
    def __init__(self, hotkey: str, callback: Callable[[], None]) -> None:
        self.hotkey = hotkey
        self.callback = callback
        self._registered = False

    def start(self) -> None:
        if self._registered:
            return
        keyboard.add_hotkey(self.hotkey, self.callback, suppress=False, trigger_on_release=False)
        self._registered = True

    def stop(self) -> None:
        if not self._registered:
            return
        keyboard.clear_all_hotkeys()
        self._registered = False
