"""Shared application bootstrap — creates the core objects used by both CLI and GUI."""

from core.audio_input import SpeechRecognizer
from core.audio_output import Speaker
from core.event_bus import EventBus
from core.intent_router import IntentRouter
from core.plugin_loader import load_plugins
from core.wake_word import WakeWordDetector

WAKE_WORD = "hey_jarvis"


def create_context():
    """Create and wire up the core services. Returns (bus, router, speaker, recognizer, wake_detector)."""
    bus = EventBus()
    router = IntentRouter()
    speaker = Speaker()
    recognizer = SpeechRecognizer()
    wake_detector = WakeWordDetector(wake_words=[WAKE_WORD], threshold=0.5)
    load_plugins(bus, router)
    return bus, router, speaker, recognizer, wake_detector
