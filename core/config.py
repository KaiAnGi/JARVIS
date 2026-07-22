"""Configuration loader — loads .env file and sets environment variables."""

import os
from pathlib import Path


def load_env():
    """Load .env file from config/ directory."""
    env_path = Path(__file__).resolve().parent.parent / "config" / ".env"
    if not env_path.exists():
        print("[CONFIG] No .env file found — using defaults")
        return

    with open(env_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and value:
                    os.environ[key] = value

    print(f"[CONFIG] Loaded .env from {env_path}")
