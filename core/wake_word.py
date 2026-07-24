"""Wake word detection using openWakeWord."""

import os
import struct
import numpy as np
import pyaudio
from openwakeword.model import Model
from openwakeword.utils import download_models


def _find_models_dir() -> str:
    """Find openWakeWord models directory without hardcoding .venv path."""
    try:
        import openwakeword
        return os.path.join(os.path.dirname(openwakeword.__file__), "resources", "models")
    except (ImportError, AttributeError):
        pass
    return os.path.join(os.path.dirname(__file__), "..", "models", "openwakeword")


class WakeWordDetector:
    def __init__(self, wake_words=None, threshold=0.5):
        self.wake_words = wake_words or ["hey_jarvis_v0.1"]
        self.threshold = threshold
        self.model = None
        self._pa = None
        self._stream = None

    def load(self):
        download_models()
        models_dir = _find_models_dir()
        model_paths = []
        for w in self.wake_words:
            name = w if w.endswith(".onnx") else f"{w}.onnx"
            path = os.path.join(models_dir, name)
            if os.path.exists(path):
                model_paths.append(path)
            else:
                print(f"[WAKE] Model not found: {path}")
        if not model_paths:
            raise FileNotFoundError("No wake word models found")
        self.model = Model(wakeword_models=model_paths)

    def start_listening(self):
        if self.model is None:
            self.load()
        self._pa = pyaudio.PyAudio()
        self._stream = self._pa.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=1280,
        )

    def stop_listening(self):
        if self._stream:
            self._stream.stop_stream()
            self._stream.close()
        if self._pa:
            self._pa.terminate()

    def check(self) -> str | None:
        if not self._stream:
            return None
        data = self._stream.read(1280, exception_on_overflow=False)
        audio = np.frombuffer(data, dtype=np.int16)
        prediction = self.model.predict(audio)
        for wake_word, score in prediction.items():
            if score >= self.threshold:
                self.model.reset()
                return wake_word
        return None
