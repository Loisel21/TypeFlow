from __future__ import annotations

import threading
from collections.abc import Callable

import pystray
from PIL import Image

from typeflow.assets import asset_path

class TypeFlowTray:
    def __init__(self, on_show: Callable[[], None], on_hide: Callable[[], None], on_exit: Callable[[], None]) -> None:
        self._on_show = on_show
        self._on_hide = on_hide
        self._on_exit = on_exit
        self._icon = pystray.Icon(
            "TypeFlow",
            icon=self._build_icon(),
            title="TypeFlow",
            menu=pystray.Menu(
                pystray.MenuItem("Show window", self._handle_show),
                pystray.MenuItem("Send to background", self._handle_hide),
                pystray.MenuItem("Exit", self._handle_exit),
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
        tray_icon = asset_path("typeflow-tray.png")
        if tray_icon.exists():
            return Image.open(tray_icon).convert("RGBA")

        return Image.new("RGBA", (64, 64), "#12344d")
