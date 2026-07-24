"""Core audio input - Offline STT via Vosk with noise reduction."""

import json
import struct
import sys
import threading
from pathlib import Path

import numpy as np
import pyaudio
from vosk import Model, KaldiRecognizer

from core.language import MODELS, get_lang

try:
    import noisereduce as nr
    _HAS_NR = True
except ImportError:
    _HAS_NR = False

ENERGY_THRESHOLD = 500        # Minimum RMS energy to detect speech
PROP_DECREASE = 0.8           # Noise reduction strength (0=no reduction, 1=full)


class SpeechRecognizer:
    """Captures microphone audio and transcribes to text offline using Vosk."""

    MODEL_DIR = Path(__file__).parent.parent / "models"

    def __init__(self, model_name: str = None, sample_rate: int = 16000, vad_level: int = 2):
        self.sample_rate = sample_rate
        self._vad_level = vad_level
        self._nr = nr if _HAS_NR else None
        self._models = {}
        self._current_lang = get_lang()
        self._models[self._current_lang] = self._load_model(
            model_name or MODELS[self._current_lang]
        )
        self._pa = pyaudio.PyAudio()
        self._stream = None
        self._rec = None
        self._lock = threading.Lock()

    def _load_model(self, name: str) -> Model:
        path = self.MODEL_DIR / name
        if not path.exists():
            print(f"[AUDIO] Vosk model not found at: {path}")
            print("[AUDIO] Download from: https://alphacephei.com/vosk/models")
            print(f"[AUDIO] Extract the zip into: {self.MODEL_DIR}/")
            sys.exit(1)
        return Model(str(path))

    def _get_model(self, lang: str = None) -> Model:
        lang = lang or get_lang()
        if lang not in self._models:
            self._models[lang] = self._load_model(MODELS[lang])
        return self._models[lang]

    def switch_language(self):
        with self._lock:
            self.stop()
            self._current_lang = get_lang()

    def auto_detect_language(self, text: str) -> str | None:
        """Detect language from text patterns. Returns lang code or None."""
        text_lower = text.lower()
        es_markers = (
            "qué", "que", "cómo", "como", "cuál", "cual", "dónde", "donde",
            "cuándo", "cuando", "cuánto", "cuanto", "por qué", "por que",
            "necesito", "quiero", "puedes", "puedo", "abre", "busca",
            "hola", "adiós", "gracias", "ayuda", "alarma", "temporizador",
            "correo", "calendario", "reproduce", "buscar",
        )
        en_markers = (
            "what", "how", "where", "when", "why", "which", "who",
            "i need", "i want", "can you", "open", "search", "play",
            "hello", "goodbye", "thanks", "help", "alarm", "timer",
            "email", "calendar", "reproduce",
        )
        es_score = sum(1 for m in es_markers if m in text_lower)
        en_score = sum(1 for m in en_markers if m in text_lower)
        if es_score > en_score:
            return "es"
        elif en_score > es_score:
            return "en"
        return None

    def _open_stream(self):
        if self._stream is None:
            self._stream = self._pa.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=4096,
            )
            self.model = self._get_model()
            self._rec = KaldiRecognizer(self.model, self.sample_rate)

    def _is_speech(self, data: bytes) -> bool:
        """Check if audio chunk contains speech using noise reduction."""
        if not self._nr:
            return True
        audio = np.frombuffer(data, dtype=np.int16).astype(np.float32)
        reduced = nr.reduce_noise(y=audio, sr=self.sample_rate, prop_decrease=PROP_DECREASE)
        energy = np.sqrt(np.mean(reduced ** 2))
        return energy > ENERGY_THRESHOLD

    def listen_once(self) -> str:
        """Block until a complete utterance is recognized, then return text."""
        with self._lock:
            self._open_stream()
        while True:
            with self._lock:
                if self._stream is None:
                    return ""
            try:
                data = self._stream.read(4096, exception_on_overflow=False)
            except Exception:
                return ""
            if not self._is_speech(data):
                continue
            with self._lock:
                if self._rec is None:
                    return ""
                if self._rec.AcceptWaveform(data):
                    result = json.loads(self._rec.Result())
                    text = result.get("text", "").strip()
                    if text:
                        return text

    def listen_once_auto_lang(self) -> tuple[str, str]:
        """Like listen_once but returns (text, detected_lang)."""
        with self._lock:
            self._open_stream()
        while True:
            with self._lock:
                if self._stream is None:
                    return "", ""
            try:
                data = self._stream.read(4096, exception_on_overflow=False)
            except Exception:
                return "", ""
            if not self._is_speech(data):
                continue
            with self._lock:
                if self._rec is None:
                    return "", ""
                if self._rec.AcceptWaveform(data):
                    result = json.loads(self._rec.Result())
                    text = result.get("text", "").strip()
                    if text:
                        detected = self.auto_detect_language(text)
                        return text, detected or self._current_lang

    def set_vad_level(self, level: int):
        """Set noise reduction aggressiveness (0-3). 0=least, 3=most."""
        self._vad_level = max(0, min(3, level))

    def stop(self):
        if self._stream:
            self._stream.stop_stream()
            self._stream.close()
            self._stream = None

    def cleanup(self):
        self.stop()
        self._pa.terminate()
