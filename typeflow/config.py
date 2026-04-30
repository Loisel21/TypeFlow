from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path


CONFIG_PATH = Path(__file__).resolve().parents[1] / "settings.json"


@dataclass(slots=True)
class AppConfig:
    hotkey: str = "ctrl+shift+space"
    sample_rate: int = 16000
    channels: int = 1
    whisper_model: str = "small"
    language: str = "de"
    device: str = "cpu"
    compute_type: str = "int8"
    beam_size: int = 5
    paste_mode: str = "typing"
    output_mode: str = "normal"
    enhancement_mode: str = "balanced"
    translation_mode: str = "off"
    start_minimized: bool = False
    privacy_mode: bool = True
    remove_fillers: bool = True
    auto_stop_enabled: bool = True
    silence_timeout_seconds: float = 1.8
    max_recording_seconds: float = 20.0
    voice_activity_threshold: float = 0.015
    custom_replacements: dict[str, str] = field(default_factory=lambda: {"type flow": "TypeFlow"})
    snippets: dict[str, str] = field(default_factory=dict)

    @classmethod
    def load(cls) -> "AppConfig":
        if not CONFIG_PATH.exists():
            return cls()

        try:
            data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return cls()

        valid_keys = {field.name for field in cls.__dataclass_fields__.values()}
        filtered = {key: value for key, value in data.items() if key in valid_keys}
        return cls(**filtered)

    def save(self) -> None:
        CONFIG_PATH.write_text(
            json.dumps(asdict(self), indent=2, ensure_ascii=True),
            encoding="utf-8",
        )
