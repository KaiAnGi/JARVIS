<p align="center">
  <img src="https://media.tenor.com/L1mpKAWYQqUAAAAC/iron-man-iron-man-helmet.gif" width="200" alt="Iron Man Helmet"/>
</p>

<h1 align="center">J.A.R.V.I.S.</h1>

<p align="center">
  <b>Just A Rather Very Intelligent System</b><br>
  <i>Offline Voice Assistant — Powered by Python</i>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.13+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/Platform-Windows-0078D4?style=for-the-badge&logo=windows&logoColor=white" alt="Windows"/>
  <img src="https://img.shields.io/badge/Language-ES%20%7C%20EN-FF6B00?style=for-the-badge" alt="Languages"/>
  <img src="https://img.shields.io/badge/License-MIT-00FF88?style=for-the-badge" alt="MIT"/>
</p>

<p align="center">
  A fully offline, free voice assistant inspired by Tony Stark's AI.<br>
  Say <b>"Hey Jarvis"</b> to activate — no cloud APIs, no subscriptions, 100% local.
</p>

---

## ✨ Features

<table>
  <tr>
    <td><b>🎤 Voice Activation</b></td>
    <td>Wake word detection with openWakeWord — say "Hey Jarvis" to start</td>
  </tr>
  <tr>
    <td><b>🗣️ Bilingual</b></td>
    <td>Full support for <b>Spanish</b> and <b>English</b> — switch with one click</td>
  </tr>
  <tr>
    <td><b>⏱️ Time & Date</b></td>
    <td>Current time, date, and calendar info</td>
  </tr>
  <tr>
    <td><b>🔢 Calculator</b></td>
    <td>Basic math with spoken numbers (e.g., "cinco más tres")</td>
  </tr>
  <tr>
    <td><b>🖥️ System Control</b></td>
    <td>Open/close apps, minimize/maximize windows, file explorer</td>
  </tr>
  <tr>
    <td><b>🌐 Browser</b></td>
    <td>Google search, YouTube search & play, open any URL</td>
  </tr>
  <tr>
    <td><b>📦 Git Control</b></td>
    <td>git status, commit, push, pull, log</td>
  </tr>
  <tr>
    <td><b>📝 VS Code</b></td>
    <td>Open VS Code, projects, and files</td>
  </tr>
  <tr>
    <td><b>📧 Gmail</b></td>
    <td>Read/unread email count, check recent emails</td>
  </tr>
  <tr>
    <td><b>📅 Calendar</b></td>
    <td>List events, next event from Google Calendar</td>
  </tr>
</table>

---

## 🏗️ Architecture

```
app.py                         ← Desktop entry point (PyQt6 + System Tray)
├── core/
│   ├── audio_input.py         ← Vosk STT (offline speech recognition)
│   ├── audio_output.py        ← SAPI5 TTS (text-to-speech)
│   ├── event_bus.py           ← Pub/sub event system
│   ├── intent_router.py       ← Longest-pattern-match routing
│   ├── plugin_loader.py       ← Auto-discovers plugins/
│   ├── language.py            ← Bilingual manager (ES/EN)
│   ├── credentials_manager.py ← Google OAuth2
│   └── wake_word.py           ← openWakeWord (ONNX)
├── gui/
│   ├── main_window.py         ← HUD Iron Man interface
│   ├── widgets.py             ← Arc Reactor animation
│   ├── styles.py              ← Dark theme with orange/blue
│   └── tray.py                ← System tray icon
└── plugins/
    ├── datetime_calc/         ← Time, date, calculator
    ├── system_control/        ← Apps, windows, explorer
    ├── browser/               ← Google, YouTube, URLs
    ├── git_control/           ← Git commands
    ├── vscode_control/        ← VS Code integration
    ├── gmail/                 ← Email (OAuth)
    ├── calendar/              ← Events (OAuth)
    └── media_player/          ← Stub
```

---

## 🚀 Quick Start

### Prerequisites
- **Windows 10/11**
- **Python 3.13+**
- **Microphone + speakers**

### Installation

```bash
# Clone the repository
git clone https://github.com/KaiAnGi/LocalVoiceAssistant.git
cd LocalVoiceAssistant

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download Vosk models (Spanish + English)
# Extract to models/ folder
```

### Run

```bash
python app.py
```

Or double-click the **J.A.R.V.I.S.** shortcut on your desktop.

---

## 🎯 Usage

| Step | Action |
|------|--------|
| 1️⃣ | Say **"Hey Jarvis"** (or click **ACTIVATE**) |
| 2️⃣ | Speak your command |
| 3️⃣ | Jarvis responds and stays in session |
| 4️⃣ | Say **"Adiós Jarvis"** to end session |

### Example Commands

<details>
<summary><b>🇪🇸 Spanish</b></summary>

- "¿Qué hora es?"
- "¿Qué fecha hay hoy?"
- "Calcula cinco más tres"
- "Abre notepad"
- "Busca Python en Google"
- "¿Qué hay en mi calendario?"

</details>

<details>
<summary><b>🇺🇸 English</b></summary>

- "What time is it?"
- "What's the date?"
- "Calculate five plus three"
- "Open notepad"
- "Search Python on Google"
- "What's on my calendar?"

</details>

---

## 🔌 Adding a Plugin

**1. Create** `plugins/my_plugin/plugin.py`:

```python
def init(bus):
    pass

def handle(action: str, text: str, bus):
    bus.emit("speak", "Response here")
```

**2. Add patterns** in `core/language.py` → `INTENT_PATTERNS`.

**3. Restart** Jarvis — plugins are auto-discovered.

---

## 🔐 Google APIs (Gmail/Calendar)

1. Create a project in [Google Cloud Console](https://console.cloud.google.com/)
2. Enable **Gmail API** and **Calendar API**
3. Create **OAuth 2.0 credentials** (Desktop app)
4. Add your email as a **test user** in OAuth consent screen
5. Download `credentials.json` → place in `config/`
6. First run will open browser for authorization

---

## 📁 Project Structure

```
LocalVoiceAssistant/
├── app.py                  ← Desktop entry point
├── main.py                 ← CLI entry point
├── requirements.txt        ← Dependencies
├── assets/
│   └── jarvis.ico          ← Iron Man icon
├── config/
│   ├── credentials.json    ← Google OAuth (gitignored)
│   └── token.json          ← Google token (gitignored)
├── models/
│   ├── vosk-model-small-es-0.42/   ← Spanish STT
│   └── vosk-model-small-en-us-0.15/ ← English STT
├── core/                   ← Core modules
├── gui/                    ← PyQt6 interface
└── plugins/                ← Voice command plugins
```

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **STT** | [Vosk](https://alphacephei.com/vosk/) (offline, multilingual) |
| **TTS** | Windows SAPI5 (Helena ES / Zira EN) |
| **Wake Word** | [openWakeWord](https://github.com/dscripka/openWakeWord) (ONNX) |
| **GUI** | PyQt6 + Custom HUD Theme |
| **System Tray** | pystray |
| **OAuth** | Google APIs (Gmail, Calendar) |

---

## 📄 License

MIT License — use freely, modify freely.

---

<p align="center">
  <i>"I am Iron Man."</i> — Tony Stark
</p>
