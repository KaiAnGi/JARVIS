"""Configuration loader — loads .env file and sets environment variables."""

from pathlib import Path

from dotenv import load_dotenv


def load_env():
    """Load .env file from config/ directory."""
    env_path = Path(__file__).resolve().parent.parent / "config" / ".env"
    if not env_path.exists():
        print("[CONFIG] No .env file found — using defaults")
        return

    load_dotenv(env_path, override=False)
    print(f"[CONFIG] Loaded .env from {env_path}")
