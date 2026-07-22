"""Shared OAuth2 credential management for Google APIs."""

from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

CONFIG_DIR = Path(__file__).parent.parent / "config"
CREDENTIALS_FILE = CONFIG_DIR / "credentials.json"
TOKEN_FILE = CONFIG_DIR / "token.json"

ALL_SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/calendar",
]


def get_credentials(scopes: list[str] = None) -> Credentials | None:
    if scopes is None:
        scopes = ALL_SCOPES
    creds = None
    if TOKEN_FILE.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), scopes)
        except Exception:
            creds = None
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                creds = None
        if not creds:
            if not CREDENTIALS_FILE.exists():
                print("[AUTH] credentials.json not found in config/")
                return None
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(CREDENTIALS_FILE), ALL_SCOPES
                )
                creds = flow.run_local_server(port=0)
            except Exception as e:
                print(f"[AUTH] OAuth flow failed: {e}")
                return None
        try:
            TOKEN_FILE.write_text(creds.to_json())
        except Exception:
            pass
    return creds
