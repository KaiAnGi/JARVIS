"""Core audio output - Offline TTS via Windows SAPI5."""

import threading
import queue

import pythoncom
import win32com.client


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
            voices = voice.GetVoices()
            for i in range(voices.Count):
                v = voices.Item(i)
                if "Spanish" in v.GetDescription() or "español" in v.GetDescription().lower():
                    voice.Voice = v
                    break
            while True:
                text = self._queue.get()
                if text is None:
                    break
                voice.Speak(str(text), 0)
        except Exception as e:
            print(f"[SPEAKER] ERROR: {e}")
        finally:
            pythoncom.CoUninitialize()

    def speak(self, text: str):
        self._queue.put(text)

    def shutdown(self):
        self._queue.put(None)
        self._thread.join(timeout=5)

    def set_rate(self, rate: int):
        self._rate = rate

    def set_volume(self, volume: float):
        self._volume = max(0.0, min(1.0, volume))
