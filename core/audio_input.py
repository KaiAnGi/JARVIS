"""Core audio input - Offline STT via Vosk."""

import json
import sys
from pathlib import Path

import pyaudio
from vosk import Model, KaldiRecognizer

from core.language import MODELS, get_lang


class SpeechRecognizer:
    """Captures microphone audio and transcribes to text offline using Vosk."""

    MODEL_DIR = Path(__file__).parent.parent / "models"

    def __init__(self, model_name: str = None, sample_rate: int = 16000):
        self.sample_rate = sample_rate
        model_name = model_name or MODELS[get_lang()]
        self.model = self._load_model(model_name)
        self._pa = pyaudio.PyAudio()
        self._stream = None
        self._rec = None

    def _load_model(self, name: str) -> Model:
        path = self.MODEL_DIR / name
        if not path.exists():
            print(f"[AUDIO] Vosk model not found at: {path}")
            print("[AUDIO] Download from: https://alphacephei.com/vosk/models")
            print(f"[AUDIO] Extract the zip into: {self.MODEL_DIR}/")
            sys.exit(1)
        return Model(str(path))

    def switch_language(self):
        """Reload the Vosk model for the current language."""
        self.stop()
        self.model = self._load_model(MODELS[get_lang()])

    def _open_stream(self):
        if self._stream is None:
            self._stream = self._pa.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=4096,
            )
            self._rec = KaldiRecognizer(self.model, self.sample_rate)

    def listen_once(self) -> str:
        """Block until a complete utterance is recognized, then return text."""
        self._open_stream()
        while True:
            data = self._stream.read(4096, exception_on_overflow=False)
            if self._rec.AcceptWaveform(data):
                result = json.loads(self._rec.Result())
                text = result.get("text", "").strip()
                if text:
                    return text

    def listen_continuous(self, callback, stop_event=None):
        """Stream audio forever, calling callback(text) per utterance."""
        self._open_stream()
        while stop_event is None or not stop_event.is_set():
            data = self._stream.read(4096, exception_on_overflow=False)
            if self._rec.AcceptWaveform(data):
                result = json.loads(self._rec.Result())
                text = result.get("text", "").strip()
                if text:
                    callback(text)

    def stop(self):
        if self._stream:
            self._stream.stop_stream()
            self._stream.close()
            self._stream = None

    def cleanup(self):
        self.stop()
        self._pa.terminate()
