<p align="center">
  <img src="https://i.pinimg.com/originals/79/21/f0/7921f0ae664a6f24cde477a06f650e01.gif" width="200" alt="Iron Man Helmet"/>
</p>

<h1 align="center">J.A.R.V.I.S.</h1>

<p align="center">
  <b>Just A Rather Very Intelligent System</b><br>
  <i>Local Voice Assistant — Powered by Python</i>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.13+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/Platform-Windows-0078D4?style=for-the-badge&logo=windows&logoColor=white" alt="Windows"/>
  <img src="https://img.shields.io/badge/Language-ES%20%7C%20EN-FF6B00?style=for-the-badge" alt="Languages"/>
  <img src="https://img.shields.io/badge/License-MIT-00FF88?style=for-the-badge" alt="MIT"/>
</p>

<p align="center">
  A fully offline, free voice assistant inspired by Tony Stark's AI.<br>
  Say <b>"Hey Jarvis"</b> to activate — no paid APIs, no subscriptions, 100% local.
</p>

---

## Features

| Feature | Description |
|---------|-------------|
| **Voice Activation** | Wake word detection with openWakeWord — say "Hey Jarvis" |
| **Bilingual** | Full support for **Spanish** and **English** — switch with voice or click |
| **Time & Date** | Current time, date, and calculator |
| **System Control** | Open any installed app, minimize/maximize/close windows, file explorer |
| **Browser** | Google search, YouTube search & play, open any URL |
| **Tabs** | Close, new, duplicate, switch, reopen tabs + address bar focus |
| **Alarms & Timers** | Set alarms (with repetition), countdown timers, stopwatch |
| **Clipboard** | Read, copy, paste from system clipboard |
| **Screenshots** | Full screen or region capture, saved to file |
| **Spotify** | Play/pause, next/previous, volume, status, search & play songs |
| **Git** | git status, commit, push, pull, log |
| **VS Code** | Open VS Code, projects, and files |
| **Gmail** | Read/unread email count, check recent emails (OAuth) |
| **Calendar** | List events, next event from Google Calendar (OAuth) |
| **Weather** | Current weather and temperature by city |
| **Translator** | Translate between Spanish and English |
| **Discord** | Send messages/notifications to Discord via webhook |
| **Chitchat** | Greetings, jokes, status, compliments |
| **Command History** | Review past voice commands |
| **Fuzzy Intent** | Unrecognized commands are understood via local LLM (Ollama) |
| **Help** | Interactive help by category |

---

## Architecture

```
app.py                         ← Desktop entry point (PyQt6 + System Tray)
main.py                        ← CLI entry point
launch.bat                     ← One-click launcher (creates venv, installs deps, runs)
├── core/
│   ├── audio_input.py         ← Vosk STT + noise reduction (offline)
│   ├── audio_output.py        ← SAPI5 TTS (text-to-speech)
│   ├── config.py              ← .env loader (python-dotenv)
│   ├── database.py            ← SQLite command history + favorites
│   ├── event_bus.py           ← Pub/sub event system (exception-safe)
│   ├── favorites.py           ← Favorite websites manager
│   ├── fuzzy_intent.py        ← Ollama LLM for unmatched commands
│   ├── intent_router.py       ← Longest-pattern-match routing
│   ├── language.py            ← Bilingual manager (ES/EN) + all intent patterns
│   ├── logger.py              ← Structured logging with daily rotation
│   ├── ollama_client.py       ← Local LLM inference client
│   ├── plugin_loader.py       ← Auto-discovers plugins/
│   ├── credentials_manager.py ← Google OAuth2
│   └── wake_word.py           ← openWakeWord (ONNX)
├── gui/
│   ├── main_window.py         ← HUD Iron Man interface
│   ├── widgets.py             ← Arc Reactor + StatusIndicator
│   ├── styles.py              ← Dark theme with orange/blue accents
│   └── tray.py                ← System tray icon
├── plugins/
│   ├── browser/               ← Google, YouTube, URLs
│   ├── calendar/              ← Google Calendar events
│   ├── chitchat/              ← Greetings, jokes, status
│   ├── clipboard/             ← Read, copy, paste
│   ├── clock/                 ← Alarms, timers, stopwatch
│   ├── command_history/       ← Review past commands
│   ├── datetime_calc/         ← Time, date, calculator
│   ├── discord_notify/        ← Discord webhook messages
│   ├── git_control/           ← Git commands
│   ├── gmail/                 ← Email (OAuth)
│   ├── help/                  ← Interactive help
│   ├── language_control/      ← Language switching
│   ├── screenshot/            ← Screen capture
│   ├── spotify_control/       ← Spotify playback control
│   ├── system_control/        ← Apps, windows, explorer
│   ├── tab_control/           ← Browser tab management
│   ├── translator/            ← Spanish ↔ English
│   ├── vscode_control/        ← VS Code integration
│   └── weather/               ← Weather info
├── config/
│   ├── .env.example           ← API keys template
│   ├── credentials.json       ← Google OAuth (gitignored)
│   ├── token.json             ← Google token (gitignored)
│   ├── user_apps.json         ← Personal app paths (gitignored)
│   └── user_apps.json.example ← Template for custom apps
├── data/
│   └── jarvis.db              ← SQLite database (gitignored)
└── models/
    ├── vosk-model-small-es-0.42/   ← Spanish STT
    └── vosk-model-small-en-us-0.15/ ← English STT
```

---

## Quick Start

### Prerequisites
- **Windows 10/11**
- **Python 3.13+**
- **Microphone + speakers**
- **Ollama** (optional — for fuzzy intent / natural language commands)

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

# Download Vosk models
# Extract to models/ folder:
#   models/vosk-model-small-es-0.42/
#   models/vosk-model-small-en-us-0.15/

# (Optional) Set up API keys
copy config\.env.example config\.env
# Edit config\.env with your values
```

### Run

```bash
# Option 1: Double-click launch.bat (auto-setup + run)
launch.bat

# Option 2: Manual
python app.py
```

---

## Usage

| Step | Action |
|------|--------|
| 1 | Say **"Hey Jarvis"** (or click **ACTIVATE**) |
| 2 | Speak your command |
| 3 | Jarvis responds and stays in session |
| 4 | Say **"Goodbye Jarvis"** to end session |

### All Commands

<details>
<summary><b>Spanish</b></summary>

#### Hora y Fecha
| Comando | Descripción |
|---------|-------------|
| "Que hora es" | Dice la hora actual |
| "Que fecha hay hoy" | Dice la fecha de hoy |
| "Calcula cinco mas tres" | Realiza una operacion matematica |

#### Control del Sistema
| Comando | Descripción |
|---------|-------------|
| "Abre notepad" | Abre una aplicacion |
| "Abre el explorador" | Abre el explorador de archivos |
| "Minimizar" | Minimiza la ventana activa |
| "Maximizar" | Maximiza la ventana activa |
| "Cierra ventana" | Cierra la ventana activa |

#### Navegador Web
| Comando | Descripción |
|---------|-------------|
| "Busca Python en Google" | Busca en Google |
| "Busca recetas en YouTube" | Busca en YouTube |
| "Reproduce musica en YouTube" | Reproduce en YouTube |
| "Abre sitio web github.com" | Abre un sitio web |

#### Control de Pestanas
| Comando | Descripción |
|---------|-------------|
| "Cierra pestana" | Cierra la pestana actual |
| "Nueva pestana" | Abre una pestana nueva |
| "Duplica pestana" | Duplica la pestana actual |
| "Cambia pestana" | Abre el selector de pestanas |
| "Reabre pestana" | Restaura pestana cerrada |
| "Barra de direcciones" | Enfoca la barra de direcciones |

#### Alarma y Temporizador
| Comando | Descripción |
|---------|-------------|
| "Alarma a las ocho" | Pone una alarma |
| "Cancelar alarma" | Cancela la ultima alarma |
| "Lista alarmas" | Lista todas las alarmas activas |
| "Temporizador cinco minutos" | Inicia un temporizador |
| "Parar temporizador" | Detiene el temporizador |
| "Iniciar cronometro" | Inicia el cronometro |
| "Parar cronometro" | Detiene el cronometro |
| "Leer cronometro" | Dice el tiempo transcurrido |
| "Reiniciar cronometro" | Reinicia el cronometro |

#### Portapapeles
| Comando | Descripción |
|---------|-------------|
| "Lee portapapeles" | Lee el contenido del portapapeles |
| "Copiar" | Copia texto al portapapeles |
| "Pegar" | Pega del portapapeles |

#### Captura de Pantalla
| Comando | Descripción |
|---------|-------------|
| "Captura" | Toma una captura de pantalla completa |
| "Captura de region" | Captura una region especifica |

#### Spotify
| Comando | Descripción |
|---------|-------------|
| "Pausa musica" | Pausa la reproduccion |
| "Reanuda musica" | Reanuda la reproduccion |
| "Siguiente cancion" | Siguiente tema |
| "Cancion anterior" | Tema anterior |
| "Volumen" | Ajusta el volumen |
| "Que suena" | Informa la cancion actual |
| "Reproduce en spotify cancion" | Busca y reproduce una cancion |

#### Git
| Comando | Descripción |
|---------|-------------|
| "git status" | Estado del repositorio |
| "git commit" | Confirma cambios |
| "git push" | Sube al remote |
| "git pull" | Baja del remote |
| "git log" | Ultimos commits |

#### VS Code
| Comando | Descripción |
|---------|-------------|
| "Abre vscode" | Abre VS Code |
| "Abre proyecto" | Abre un proyecto |
| "Abre archivo" | Abre un archivo |

#### Gmail
| Comando | Descripción |
|---------|-------------|
| "Cuantos correos" | Cuenta correos sin leer |
| "Revisa correo" | Muestra correos recientes |
| "Lee correo" | Lee un correo especifico |

#### Calendario
| Comando | Descripción |
|---------|-------------|
| "Que hay en mi calendario" | Lista proximos eventos |
| "Que sigue" | Muestra el siguiente evento |

#### Clima
| Comando | Descripción |
|---------|-------------|
| "Clima" | Clima actual de tu ubicacion |
| "Clima en Madrid" | Clima en una ciudad |

#### Traductor
| Comando | Descripción |
|---------|-------------|
| "Traduce hola al ingles" | Traduce texto al ingles |
| "Traduce hello al espanol" | Traduce texto al espanol |

#### Discord
| Comando | Descripción |
|---------|-------------|
| "Enviar a discord" | Envia un mensaje a Discord |
| "Notificar discord" | Envia una notificacion |

#### Historial
| Comando | Descripción |
|---------|-------------|
| "Ultimo comando" | Dice el ultimo comando ejecutado |
| "Historial de comandos" | Lista los ultimos comandos |
| "Borrar historial" | Limpia el historial |

#### Idioma
| Comando | Descripción |
|---------|-------------|
| "Cambiar idioma" | Alterna entre espanol e ingles |
| "Habla espanol" | Cambia a espanol |
| "Habla ingles" | Cambia a ingles |

#### Ayuda
| Comando | Descripción |
|---------|-------------|
| "Ayuda" | Lista categorias de ayuda |
| "Ayuda con navegador" | Detalles de una categoria |

#### Chitchat
| Comando | Descripción |
|---------|-------------|
| "Hola" | Saludo |
| "Cuentame un chiste" | Dice un chiste |
| "Quien eres" | Se presenta |

#### Salir
| Comando | Descripción |
|---------|-------------|
| "Adios Jarvis" | Termina la sesion y oculta la ventana |

</details>

<details>
<summary><b>English</b></summary>

#### Time & Date
| Command | Description |
|---------|-------------|
| "What time is it" | Tells current time |
| "What's the date" | Tells today's date |
| "Calculate five plus three" | Performs math calculation |

#### System Control
| Command | Description |
|---------|-------------|
| "Open notepad" | Opens an application |
| "Open explorer" | Opens file explorer |
| "Minimize" | Minimizes active window |
| "Maximize" | Maximizes active window |
| "Close window" | Closes active window |

#### Web Browser
| Command | Description |
|---------|-------------|
| "Search Python on Google" | Searches Google |
| "Search recipes on YouTube" | Searches YouTube |
| "Play music on YouTube" | Plays on YouTube |
| "Open website github.com" | Opens a website |

#### Tab Control
| Command | Description |
|---------|-------------|
| "Close tab" | Closes current tab |
| "New tab" | Opens new tab |
| "Duplicate tab" | Duplicates current tab |
| "Switch tab" | Opens tab picker |
| "Reopen tab" | Restores closed tab |
| "Address bar" | Focuses address bar |

#### Alarms & Timers
| Command | Description |
|---------|-------------|
| "Set alarm at eight" | Sets an alarm |
| "Cancel alarm" | Cancels the last alarm |
| "List alarms" | Lists all active alarms |
| "Timer five minutes" | Starts a countdown |
| "Stop timer" | Stops the timer |
| "Start stopwatch" | Starts the stopwatch |
| "Stop stopwatch" | Stops the stopwatch |
| "Read stopwatch" | Reports elapsed time |
| "Reset stopwatch" | Resets the stopwatch |

#### Clipboard
| Command | Description |
|---------|-------------|
| "Read clipboard" | Reads clipboard content |
| "Copy to clipboard" | Copies text to clipboard |
| "Paste" | Pastes from clipboard |

#### Screenshot
| Command | Description |
|---------|-------------|
| "Take screenshot" | Captures full screen |
| "Screenshot area" | Captures a specific region |

#### Spotify
| Command | Description |
|---------|-------------|
| "Pause music" | Pauses playback |
| "Resume music" | Resumes playback |
| "Next song" | Next track |
| "Previous song" | Previous track |
| "Volume" | Adjusts volume |
| "What's playing" | Reports current song |
| "Play on spotify song" | Searches and plays a song |

#### Git
| Command | Description |
|---------|-------------|
| "git status" | Repository status |
| "git commit" | Commit changes |
| "git push" | Push to remote |
| "git pull" | Pull from remote |
| "git log" | Recent commits |

#### VS Code
| Command | Description |
|---------|-------------|
| "Open vscode" | Opens VS Code |
| "Open project" | Opens a project |
| "Open file" | Opens a file |

#### Gmail
| Command | Description |
|---------|-------------|
| "How many emails" | Counts unread emails |
| "Check email" | Shows recent emails |
| "Read email" | Reads specific email |

#### Calendar
| Command | Description |
|---------|-------------|
| "What's on my calendar" | Lists upcoming events |
| "What's next" | Shows next event |

#### Weather
| Command | Description |
|---------|-------------|
| "Weather" | Current weather at your location |
| "Weather in London" | Weather in a city |

#### Translator
| Command | Description |
|---------|-------------|
| "Translate hello to Spanish" | Translates text to Spanish |
| "Translate hola to English" | Translates text to English |

#### Discord
| Command | Description |
|---------|-------------|
| "Send to Discord" | Sends a message to Discord |
| "Notify Discord" | Sends a notification |

#### Command History
| Command | Description |
|---------|-------------|
| "Last command" | Reports the last executed command |
| "Command history" | Lists recent commands |
| "Clear history" | Clears command history |

#### Language
| Command | Description |
|---------|-------------|
| "Switch language" | Toggles between English and Spanish |
| "Speak Spanish" | Switches to Spanish |
| "Speak English" | Switches to English |

#### Help
| Command | Description |
|---------|-------------|
| "Help" | Lists help categories |
| "Help with browser" | Details for a category |

#### Chitchat
| Command | Description |
|---------|-------------|
| "Hello" | Greeting |
| "Tell me a joke" | Tells a joke |
| "Who are you" | Introduces itself |

#### Exit
| Command | Description |
|---------|-------------|
| "Goodbye Jarvis" | Ends session and hides window |

</details>

---

## Adding a Plugin

**1. Create** `plugins/my_plugin/plugin.py`:

```python
def init(bus):
    pass

def handle(action: str, text: str, bus):
    bus.emit("speak", "Response here")
```

**2. Add patterns** in `core/language.py` inside `INTENT_PATTERNS`:

```python
"my_plugin": {
    "my_action": {"en": ["my phrase"], "es": ["mi frase"]},
},
```

**3. (Optional)** Create `plugins/my_plugin/manifest.json`:

```json
{
  "name": "my_plugin",
  "version": "1.0.0",
  "description": "My custom plugin",
  "intents": [
    {"pattern": "my phrase", "action": "my_action"}
  ]
}
```

**4. Restart** Jarvis — plugins are auto-discovered.

---

## Google APIs (Gmail/Calendar)

1. Create a project in [Google Cloud Console](https://console.cloud.google.com/)
2. Enable **Gmail API** and **Calendar API**
3. Create **OAuth 2.0 credentials** (Desktop app)
4. Add your email as a **test user** in OAuth consent screen
5. Download `credentials.json` -> place in `config/`
6. First run will open browser for authorization

---

## Custom Apps

To add your own app shortcuts, create `config/user_apps.json` (gitignored):

```json
{
  "myapp": "C:\\Path\\To\\app.exe",
  "mygame": "D:\\Games\\game.exe"
}
```

Then say "abre myapp" or "open myapp". See `config/user_apps.json.example` for a template.

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| **STT** | [Vosk](https://alphacephei.com/vosk/) (offline, multilingual) |
| **TTS** | Windows SAPI5 (Helena ES / Zira EN) |
| **Wake Word** | [openWakeWord](https://github.com/dscripka/openWakeWord) (ONNX) |
| **LLM** | [Ollama](https://ollama.com/) (optional, for fuzzy intent) |
| **Noise Reduction** | [noisereduce](https://github.com/timsainb/noisereduce) |
| **GUI** | PyQt6 + Custom HUD Theme |
| **System Tray** | pystray |
| **OAuth** | Google APIs (Gmail, Calendar) |
| **Database** | SQLite (command history, favorites) |
| **Config** | python-dotenv (.env files) |

---

## License

MIT License — use freely, modify freely.

---

<p align="center">
  <i>"The truth is... I am Iron Man"</i> — Tony Stark
</p>
