"""Ollama client for local LLM inference."""

import json
import os
import urllib.request

OLLAMA_URL = "http://localhost:11434"
MODEL = os.environ.get("JARVIS_OLLAMA_MODEL", "qwen3:8b")


def is_available() -> bool:
    """Check if Ollama is running and reachable."""
    try:
        req = urllib.request.Request(f"{OLLAMA_URL}/api/tags")
        with urllib.request.urlopen(req, timeout=3) as resp:
            return resp.status == 200
    except Exception:
        return False


def chat(prompt: str, system: str = "", timeout: int = 30) -> str:
    """Send a prompt to Ollama and return the response text.

    Uses /no_think prefix + think:false for Qwen3 compatibility.
    Safe for other models — think:false is ignored if unsupported.
    """
    full_prompt = f"/no_think\n{prompt}"
    payload = {
        "model": MODEL,
        "prompt": full_prompt,
        "stream": False,
        "think": False,
        "options": {
            "num_predict": 256,
            "temperature": 0.1,
        },
    }
    if system:
        payload["system"] = system

    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{OLLAMA_URL}/api/generate",
            data=data,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            response = result.get("response", "").strip()
            response = response.replace("<think>", "").replace("</think>", "").strip()
            return response
    except Exception as e:
        print(f"[OLLAMA] Error: {e}")
        return ""
