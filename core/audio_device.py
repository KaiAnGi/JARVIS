"""Audio input device selection — picks a microphone that produces audio."""

import os
import time

import numpy as np
import pyaudio

import core.logger as logger

SILENCE_PEAK = 10
SATURATED_PEAK = 30000
PROBE_SECONDS = 0.3

_selected = None


def _probe_peak(pa, index: int) -> float:
    stream = None
    try:
        stream = pa.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            input_device_index=index,
            frames_per_buffer=1280,
        )
        peak = 0.0
        end = time.time() + PROBE_SECONDS
        while time.time() < end:
            data = stream.read(1280, exception_on_overflow=False)
            audio = np.frombuffer(data, dtype=np.int16)
            peak = max(peak, float(np.max(np.abs(audio))))
        return peak
    except Exception:
        return 0.0
    finally:
        if stream is not None:
            try:
                stream.close()
            except Exception:
                pass


def _candidates(pa) -> list[int]:
    preferred = os.getenv("AUDIO_INPUT_DEVICE")
    names = []
    if preferred:
        try:
            return [int(preferred)]
        except ValueError:
            names = [name.strip().lower() for name in preferred.split(",") if name.strip()]

    default = None
    try:
        default = pa.get_default_input_device_info()["index"]
    except Exception:
        pass
    order = []
    if default is not None and default >= 0:
        order.append(default)
    for i in range(pa.get_device_count()):
        try:
            info = pa.get_device_info_by_index(i)
        except OSError:
            continue
        if info.get("maxInputChannels", 0) > 0:
            order.append(i)

    if names:
        filtered = []
        for i in order:
            try:
                name = pa.get_device_info_by_index(i).get("name", "").lower()
            except OSError:
                continue
            if any(n in name for n in names):
                filtered.append(i)
        order = filtered if filtered else order

    seen = set()
    result = []
    for i in order:
        if i not in seen:
            seen.add(i)
            result.append(i)
    return result


def pick_input_device() -> int:
    """Return the index of the best input device, caching the result."""
    global _selected
    if _selected is not None:
        return _selected

    pa = pyaudio.PyAudio()
    selected = None
    name = ""
    try:
        default = None
        try:
            default = pa.get_default_input_device_info()["index"]
        except Exception:
            pass
        for index in _candidates(pa):
            peak = _probe_peak(pa, index)
            if peak >= SATURATED_PEAK:
                continue
            if peak > SILENCE_PEAK:
                selected = index
                break
        else:
            selected = default
        if selected is None or selected < 0:
            selected = 0
        try:
            name = pa.get_device_info_by_index(selected).get("name", "")
        except Exception:
            pass
    finally:
        pa.terminate()

    _selected = selected
    logger.log_event("AUDIO", f"Input device selected: [{_selected}] {name}")
    return _selected
