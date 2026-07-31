# AGENTS.md

Guía para agentes que trabajan en este repositorio.

## Proyecto
Asistente de voz por voz J.A.R.V.I.S. (LocalVoiceAssistant). Stack: Python 3.13, PyQt6 (GUI), openwakeword + Vosk (STT), pyttsx3 (TTS), Ollama (fallback de intención fuzzy), SQLite (historial).

## Comandos de verificación
Todos se ejecutan con el intérprete del venv:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\ruff.exe check .
.\.venv\Scripts\python.exe -m mypy core/ plugins/ --python-version 3.13
```

- `mypy` solo cubre `core/` y `plugins/` (igual que el CI en `.github/workflows/typecheck.yml`). `gui/widgets.py` tiene errores mypy preexistentes que no deben bloquear.
- El CI (pytest) corre en `.github/workflows/tests.yml`.

## Arquitectura / convenciones
- Los plugins viven en `plugins/<nombre>/plugin.py`; exponen `handle(action, text, bus)` y opcionalmente `register(bus)`.
- `core/intent_router.py` expone `get_plugin(name)` — no acceder a `_plugins`.
- `core/command_processor.py::process_unmatched` es el fallback compartido (CLI + GUI) para texto no reconocido.
- `core/fuzzy_actions.py` es la allowlist de acciones ejecutables del LLM: solo se permite lo listado en `_PLUGIN_MAP`. Nunca ejecutar acciones arbitrarias del LLM.
- El prompt del LLM (`core/fuzzy_intent.py`) incluye mitigación anti prompt-injection; el texto del usuario siempre es dato, nunca instrucción.
- `core/bootstrap.py::create_context()` devuelve un `AppContext`; `main.py`, `app.py` y la GUI usan esa dependencia. No crear dependencias manualmente.
- Textos del usuario/líneas habladas: `resp(key, ...)` en `core/language.py`. Añadir nuevas respuestas en los dos idiomas (es/en).
- UI en `gui/`; el routing se ejecuta en un `QThreadPool` (`RouteTask`) y los eventos del bus llegan a la GUI vía `EventBridge` (nunca tocar widgets Qt desde hilos de trabajo).
- `core/database.py` y `core/favorites.py` son APIs públicas (con locks) — los plugins no deben abrir internos.
- Secrets: `core/file_secure.py::restrict_file` limita ACL a Windows; aplicar al guardar `token.json`/tokens. `core/logger.py::_redact` oculta secretos al loguear.

## Reglas
- No commitear nada sin pedirlo expresamente.
- Ejecutar siempre `pytest`, `ruff` y `mypy` (los tres de arriba) al terminar cambios.
- No añadir comentarios en el código salvo que se pidan.
