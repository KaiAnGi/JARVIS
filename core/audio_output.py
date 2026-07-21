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

    def _run_loop(self):
        pythoncom.CoInitialize()
        try:
            voice = win32com.client.Dispatch("SAPI.SpVoice")
            voice.Rate = self._rate
            voice.Volume = int(self._volume * 100)
            self._apply_voice(voice)
            while True:
                item = self._queue.get()
                if item is None:
                    break
                if item == "__switch__":
                    self._apply_voice(voice)
                elif isinstance(item, str):
                    voice.Speak(item, 0)
        except Exception as e:
            print(f"[SPEAKER] ERROR: {e}")
        finally:
            pythoncom.CoUninitialize()

    def _apply_voice(self, voice):
        voices = voice.GetVoices()
        tag = VOICES[get_lang()]
        for i in range(voices.Count):
            v = voices.Item(i)
            desc = v.GetDescription()
            if tag == "Spanish" and ("Spanish" in desc or "español" in desc.lower()):
                voice.Voice = v
                return
            elif tag == "English" and "English" in desc:
                voice.Voice = v
                return

    def switch_language(self):
        self._queue.put("__switch__")

    def speak(self, text: str):
        self._queue.put(text)

    def shutdown(self):
        self._queue.put(None)
        self._thread.join(timeout=5)

    def set_rate(self, rate: int):
        self._rate = rate

    def set_volume(self, volume: float):
        self._volume = max(0.0, min(1.0, volume))
