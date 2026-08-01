"""Wake word detection using Vosk continuous speech recognition.

The openwakeword "hey_jarvis" model does not fire on real user speech, so the
wake word is detected with a Vosk recognizer (English model, constrained
grammar, amplified input) that matches "hey jarvis".
"""

import json
import os

import numpy as np
import pyaudio
from vosk import KaldiRecognizer, Model

from core.audio_device import pick_input_device
from core.language import MODELS

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")

WAKE_LANG = "en"
WAKE_GRAMMAR = '["hey jarvis", "jarvis", "hey", "jar"]'
INPUT_GAIN = 8.0

WAKE_VARIANTS = frozenset(
    {
        "jarvis",
        "javis",
        "yarvis",
        "harvis",
        "jarviz",
        "yarvez",
        "jarbis",
        "yarbis",
        "jerbis",
        "gerbis",
        "yervis",
        "jervis",
    }
)

WAKE_PREFIXES = (
    "jarvi",
    "jarbi",
    "yarvi",
    "harvi",
    "jerbi",
    "gerbi",
    "yervi",
    "jervi",
)


class WakeWordDetector:
    def __init__(self, wake_words=None, threshold=0.5):
        self.wake_words = wake_words or ["hey_jarvis_v0.1"]
        self.threshold = threshold
        self.model = None
        self._models = {}
        self._pa = None
        self._stream = None
        self._rec = None

    def _load_model(self, lang: str) -> Model:
        if lang not in self._models:
            path = os.path.join(MODEL_DIR, MODELS[lang])
            self._models[lang] = Model(str(path))
        return self._models[lang]

    def load(self):
        self.model = self._load_model(WAKE_LANG)

    def start_listening(self):
        if self._rec is not None:
            return
        self.model = self._load_model(WAKE_LANG)
        self._pa = pyaudio.PyAudio()
        self._stream = self._pa.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            input_device_index=pick_input_device(),
            frames_per_buffer=1280,
        )
        self._rec = KaldiRecognizer(self.model, 16000, WAKE_GRAMMAR)

    def stop_listening(self):
        self._rec = None
        if self._stream is not None:
            try:
                self._stream.stop_stream()
            except Exception:
                pass
            try:
                self._stream.close()
            except Exception:
                pass
            self._stream = None
        if self._pa is not None:
            self._pa.terminate()
            self._pa = None

    def check(self) -> str | None:
        if self._stream is None or self._rec is None:
            return None
        try:
            data = self._stream.read(1280, exception_on_overflow=False)
            audio = np.frombuffer(data, dtype=np.int16).astype(np.float32) * INPUT_GAIN
            audio = np.clip(audio, -32768, 32767).astype(np.int16)
            data = audio.tobytes()
            text = ""
            if self._rec.AcceptWaveform(data):
                text = json.loads(self._rec.Result()).get("text", "")
            else:
                text = json.loads(self._rec.PartialResult()).get("partial", "")
            if self._is_wake(text):
                self._rec.Reset()
                return self.wake_words[0]
        except Exception:
            return None
        return None

    def _is_wake(self, text: str) -> bool:
        t = text.lower().strip()
        if not t:
            return False
        if "jarvis" in t.replace(" ", ""):
            return True
        return any(word in WAKE_VARIANTS or word.startswith(WAKE_PREFIXES) for word in t.split())
