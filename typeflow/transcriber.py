from __future__ import annotations

import re
from dataclasses import dataclass

import numpy as np
from faster_whisper import WhisperModel


@dataclass(slots=True)
class TranscriptResult:
    text: str
    language: str


class WhisperTranscriber:
    def __init__(
        self,
        model_name: str,
        language: str,
        device: str,
        compute_type: str,
        beam_size: int,
    ) -> None:
        self.model_name = model_name
        self.language = language
        self.device = device
        self.compute_type = compute_type
        self.beam_size = beam_size
        self._model: WhisperModel | None = None

    def transcribe(self, audio: np.ndarray) -> TranscriptResult:
        if audio.size == 0:
            return TranscriptResult(text="", language=self.language)

        model = self._get_model()
        segments, info = model.transcribe(
            audio,
            language=self.language,
            beam_size=self.beam_size,
            vad_filter=True,
        )
        text = " ".join(segment.text.strip() for segment in segments).strip()
        return TranscriptResult(text=self._clean_text(text), language=info.language or self.language)

    def _clean_text(self, text: str) -> str:
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def _get_model(self) -> WhisperModel:
        if self._model is None:
            self._model = WhisperModel(
                self.model_name,
                device=self.device,
                compute_type=self.compute_type,
            )
        return self._model
