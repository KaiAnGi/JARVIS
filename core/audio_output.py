"""Core audio output - Offline TTS via Windows SAPI5."""

import threading
import queue

import pythoncom
import win32com.client

from core.language import VOICES, get_lang


class Speaker:
    """Speaks text aloud via SAPI5 COM directly (no pyttsx3 dependency)."""

    def __init__(self, rate: int = 0, volume: float = 1.0):
        self._rate = rate
        self._volume = volume
        self._queue = queue.Queue()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        self._voice_tag = VOICES[get_lang()]

    def _run_loop(self):
        pythoncom.CoInitialize()
        try:
            self._voice = win32com.client.Dispatch("SAPI.SpVoice")
            self._voice.Rate = self._rate
            self._voice.Volume = int(self._volume * 100)
            self._apply_voice()
            while True:
                item = self._queue.get()
                if item is None:
                    break
                if isinstance(item, str):
                    self._voice.Speak(item, 0)
        except Exception as e:
            print(f"[SPEAKER] ERROR: {e}")
        finally:
            pythoncom.CoUninitialize()

    def _apply_voice(self):
        voices = self._voice.GetVoices()
        tag = VOICES[get_lang()]
        for i in range(voices.Count):
            v = voices.Item(i)
            desc = v.GetDescription()
            if tag == "Spanish" and ("Spanish" in desc or "español" in desc.lower()):
                self._voice.Voice = v
                return
            elif tag == "English" and "English" in desc:
                self._voice.Voice = v
                return

    def switch_language(self):
        """Switch TTS voice for the current language."""
        self._apply_voice()

    def speak(self, text: str):
        self._queue.put(text)

    def shutdown(self):
        self._queue.put(None)
        self._thread.join(timeout=5)

    def set_rate(self, rate: int):
        self._rate = rate

    def set_volume(self, volume: float):
        self._volume = max(0.0, min(1.0, volume))
