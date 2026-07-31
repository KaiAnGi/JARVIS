"""Shared application bootstrap — creates the core objects used by both CLI and GUI."""

from dataclasses import dataclass

from core.audio_input import SpeechRecognizer
from core.audio_output import Speaker
from core.event_bus import EventBus
from core.intent_router import IntentRouter
from core.plugin_loader import load_plugins
from core.wake_word import WakeWordDetector

WAKE_WORD = "hey_jarvis_v0.1"


@dataclass
class AppContext:
    """All wired core services shared by the CLI and GUI entry points."""

    bus: EventBus
    router: IntentRouter
    speaker: Speaker
    recognizer: SpeechRecognizer
    wake_detector: WakeWordDetector


def create_context() -> AppContext:
    """Create and wire up the core services."""
    bus = EventBus()
    router = IntentRouter()
    speaker = Speaker()
    recognizer = SpeechRecognizer()
    wake_detector = WakeWordDetector(wake_words=[WAKE_WORD], threshold=0.5)
    load_plugins(bus, router)
    return AppContext(bus, router, speaker, recognizer, wake_detector)
