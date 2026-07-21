# Jarvis - Offline Voice Assistant

A fully offline, free voice assistant built with Python. Say "Hey Jarvis" to activate, then speak your command. No cloud APIs, no subscriptions — everything runs locally on your machine.

## Features

| Plugin | Capabilities |
|--------|-------------|
| **datetime_calc** | Current time, date, calculator with spoken numbers |
| **system_control** | Open/close apps, minimize/maximize windows, file explorer |
| **browser** | Google search, YouTube search/play, open any URL |
| **git_control** | git status, commit, push, pull, log |
| **vscode_control** | Open VS Code, projects, files |
| **gmail** | Read/unread email count, check recent emails (OAuth) |
| **calendar** | List events, next event (OAuth) |
| **wake_word** | "Hey Jarvis" activation via openWakeWord |

## Architecture

```
main.py                    ← Entry point: wake word → listen → route
├── core/
│   ├── audio_input.py     ← Vosk STT
│   ├── audio_output.py    ← SAPI5 TTS (pywin32)
│   ├── event_bus.py       ← Pub/sub event system
│   ├── intent_router.py   ← Longest-pattern-match routing
│   ├── plugin_loader.py   ← Auto-discovers plugins/
│   ├── credentials_manager.py ← Google OAuth2
│   └── wake_word.py       ← openWakeWord (ONNX)
└── plugins/
    ├── datetime_calc/
    ├── system_control/
    ├── browser/
    ├── git_control/
    ├── vscode_control/
    ├── gmail/
    ├── calendar/
    └── media_player/      ← Stub
```

## Requirements

- Windows 10/11
- Python 3.13+
- Microphone + speakers

## Installation

```bash
git clone https://github.com/KaiAnGi/LocalVoiceAssistant.git
cd LocalVoiceAssistant
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Download the Vosk model (small, ~50MB):
```bash
# Download vosk-model-small-en-us-0.15 and extract to models/
```

## Usage

```bash
python main.py
```

1. Say **"Hey Jarvis"** to activate
2. Speak your command (e.g., "what time is it", "open YouTube", "git status")
3. Jarvis responds and returns to listening for the wake word

## Adding a New Plugin

1. Create `plugins/my_plugin/manifest.json`:
```json
{
  "name": "my_plugin",
  "version": "1.0.0",
  "intents": [
    {"action": "my_action", "patterns": ["my pattern"]}
  ]
}
```

2. Create `plugins/my_plugin/plugin.py`:
```python
def init(bus):
    pass

def handle(action: str, text: str, bus):
    bus.emit("speak", "Response here")
```

3. Restart Jarvis — plugins are auto-discovered.

## Google APIs (Gmail/Calendar)

1. Create a project in [Google Cloud Console](https://console.cloud.google.com/)
2. Enable Gmail API and Calendar API
3. Create OAuth 2.0 credentials (Desktop app)
4. Download `credentials.json` and place in `config/`
5. First run will open a browser for authorization

## License

MIT
