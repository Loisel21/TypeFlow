from __future__ import annotations

import threading

import numpy as np
import sounddevice as sd


class AudioRecorder:
    def __init__(self, sample_rate: int, channels: int) -> None:
        self.sample_rate = sample_rate
        self.channels = channels
        self._chunks: list[np.ndarray] = []
        self._stream: sd.InputStream | None = None
        self._lock = threading.Lock()
        self._recording = False

    @property
    def is_recording(self) -> bool:
        return self._recording

    def start(self) -> None:
        with self._lock:
            if self._recording:
                return
            self._chunks = []
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

    def _on_audio(self, indata, frames, time, status) -> None:  # noqa: ANN001
        if status:
            return
        self._chunks.append(indata.copy())
