from __future__ import annotations

import threading
import time as time_module

import numpy as np
import sounddevice as sd


class AudioRecorder:
    def __init__(self, sample_rate: int, channels: int, voice_activity_threshold: float) -> None:
        self.sample_rate = sample_rate
        self.channels = channels
        self.voice_activity_threshold = voice_activity_threshold
        self._chunks: list[np.ndarray] = []
        self._stream: sd.InputStream | None = None
        self._lock = threading.Lock()
        self._recording = False
        self._recording_started_at = 0.0
        self._last_voice_at = 0.0
        self._has_detected_speech = False

    @property
    def is_recording(self) -> bool:
        return self._recording

    @property
    def has_detected_speech(self) -> bool:
        return self._has_detected_speech

    def start(self) -> None:
        with self._lock:
            if self._recording:
                return
            self._chunks = []
            now = time_module.monotonic()
            self._recording_started_at = now
            self._last_voice_at = now
            self._has_detected_speech = False
            self._stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype="float32",
                callback=self._on_audio,
            )
            self._stream.start()
            self._recording = True

    def stop(self) -> np.ndarray:
        with self._lock:
            if not self._recording:
                return np.array([], dtype=np.float32)
            assert self._stream is not None
            self._stream.stop()
            self._stream.close()
            self._stream = None
            self._recording = False

            if not self._chunks:
                return np.array([], dtype=np.float32)

            audio = np.concatenate(self._chunks, axis=0)
            if audio.ndim > 1:
                audio = audio.mean(axis=1)
            return audio.astype(np.float32, copy=False)

    def recording_elapsed(self) -> float:
        if not self._recording:
            return 0.0
        return time_module.monotonic() - self._recording_started_at

    def silence_elapsed(self) -> float:
        if not self._recording:
            return 0.0
        return time_module.monotonic() - self._last_voice_at

    def _on_audio(self, indata, frames, time, status) -> None:  # noqa: ANN001
        if status:
            return
        self._chunks.append(indata.copy())
        level = float(np.sqrt(np.mean(np.square(indata))))
        if level >= self.voice_activity_threshold:
            now = time_module.monotonic()
            self._last_voice_at = now
            self._has_detected_speech = True
