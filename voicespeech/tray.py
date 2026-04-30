from __future__ import annotations

import threading
from collections.abc import Callable

import pystray
from PIL import Image, ImageDraw


class VoiceSpeechTray:
    def __init__(self, on_show: Callable[[], None], on_hide: Callable[[], None], on_exit: Callable[[], None]) -> None:
        self._on_show = on_show
        self._on_hide = on_hide
        self._on_exit = on_exit
        self._icon = pystray.Icon(
            "VoiceSpeech",
            icon=self._build_icon(),
            title="VoiceSpeech",
            menu=pystray.Menu(
                pystray.MenuItem("Fenster anzeigen", self._handle_show),
                pystray.MenuItem("In Hintergrund senden", self._handle_hide),
                pystray.MenuItem("Beenden", self._handle_exit),
            ),
        )
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._icon.run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._icon.stop()

    def notify(self, title: str, message: str) -> None:
        try:
            self._icon.notify(message, title)
        except Exception:  # noqa: BLE001
            return

    def _handle_show(self, icon, item) -> None:  # noqa: ANN001
        self._on_show()

    def _handle_hide(self, icon, item) -> None:  # noqa: ANN001
        self._on_hide()

    def _handle_exit(self, icon, item) -> None:  # noqa: ANN001
        self._on_exit()

    def _build_icon(self) -> Image.Image:
        image = Image.new("RGBA", (64, 64), "#12344d")
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle((8, 8, 56, 56), radius=14, fill="#0f766e")
        draw.ellipse((22, 18, 42, 38), fill="white")
        draw.rectangle((29, 34, 35, 46), fill="white")
        return image
