import json
import os
import time
from urllib.parse import urlencode
import requests

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/tasks",
]


class OAuthClient:
    def __init__(self, config_path: str, token_path: str):
        with open(config_path) as f:
            config = json.load(f)
        web = config["web"]
        self.client_id = web["client_id"]
        self.client_secret = web["client_secret"]
        self.auth_uri = web["auth_uri"]
        self.token_uri = web["token_uri"]
        self.redirect_uri = web["redirect_uris"][0]
        self.token_path = token_path

    def build_auth_url(self) -> str:
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": " ".join(SCOPES),
            "access_type": "offline",
            "prompt": "consent",
        }
        return f"{self.auth_uri}?{urlencode(params)}"

    def exchange_code(self, code: str) -> dict:
        resp = requests.post(
            self.token_uri,
            data={
                "code": code,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "redirect_uri": self.redirect_uri,
                "grant_type": "authorization_code",
            },
        )
        if resp.status_code != 200:
            raise Exception(f"Token exchange failed: {resp.text}")
        token = resp.json()
        token["obtained_at"] = int(time.time())
        self._save_token(token)
        return token

    def refresh_token(self, refresh_token: str) -> dict:
        resp = requests.post(
            self.token_uri,
            data={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
            },
        )
        if resp.status_code != 200:
            raise Exception(f"Token refresh failed: {resp.text}")
        new_token = resp.json()
        new_token["obtained_at"] = int(time.time())
        new_token["refresh_token"] = refresh_token
        self._save_token(new_token)
        return new_token

    def load_token(self) -> dict | None:
        if not os.path.exists(self.token_path):
            return None
        with open(self.token_path) as f:
            return json.load(f)

    def get_valid_token(self) -> dict | None:
        token = self.load_token()
        if token is None:
            return None
        obtained_at = token.get("obtained_at", 0)
        expires_in = token.get("expires_in", 3600)
        if time.time() > obtained_at + expires_in - 60:
            rt = token.get("refresh_token")
            if rt:
                return self.refresh_token(rt)
            return None
        return token

    def _save_token(self, token: dict):
        os.makedirs(os.path.dirname(self.token_path) or ".", exist_ok=True)
        with open(self.token_path, "w") as f:
            json.dump(token, f, indent=2)
