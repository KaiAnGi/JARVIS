"""Shared OAuth2 credential management for Google APIs."""

import json
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

CONFIG_DIR = Path(__file__).parent.parent / "config"
CREDENTIALS_FILE = CONFIG_DIR / "credentials.json"
TOKEN_FILE = CONFIG_DIR / "token.json"


def get_credentials(scopes: list[str]) -> Credentials | None:
    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), scopes)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDENTIALS_FILE.exists():
                print("[AUTH] credentials.json not found in config/")
                print("[AUTH] Download from Google Cloud Console and place it there")
                return None
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_FILE), scopes
            )
            creds = flow.run_local_server(port=0)
        TOKEN_FILE.write_text(creds.to_json())
    return creds
