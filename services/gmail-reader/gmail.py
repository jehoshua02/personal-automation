import base64
import requests

GMAIL_API = "https://gmail.googleapis.com/gmail/v1/users/me"


class GmailClient:
    def __init__(self, auth_service_url: str):
        self.auth_service_url = auth_service_url
        self._label_id_cache = None

    def get_token(self) -> str:
        resp = requests.get(f"{self.auth_service_url}/token")
        if resp.status_code != 200:
            raise Exception(f"Auth service returned {resp.status_code}")
        return resp.json()["access_token"]

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self.get_token()}"}

    def fetch_messages(self, max_results: int = 10) -> list[dict]:
        resp = requests.get(
            f"{GMAIL_API}/messages",
            headers=self._headers(),
            params={"q": "-label:processed", "maxResults": max_results},
        )
        if resp.status_code != 200:
            raise Exception(f"Gmail list failed: {resp.text}")
        data = resp.json()
        message_ids = data.get("messages", [])
        messages = []
        for m in message_ids:
            msg = self._get_message(m["id"])
            if msg:
                messages.append(msg)
        return messages

    def _get_message(self, msg_id: str) -> dict | None:
        resp = requests.get(f"{GMAIL_API}/messages/{msg_id}", headers=self._headers())
        if resp.status_code != 200:
            return None
        data = resp.json()
        headers = {h["name"]: h["value"] for h in data.get("payload", {}).get("headers", [])}
        body = self._extract_body(data.get("payload", {}))
        return {
            "id": data["id"],
            "thread_id": data.get("threadId", ""),
            "from": headers.get("From", ""),
            "to": headers.get("To", ""),
            "subject": headers.get("Subject", ""),
            "date": headers.get("Date", ""),
            "body": body,
            "link": self.build_message_link(data["id"]),
        }

    def _extract_body(self, payload: dict) -> str:
        body_data = payload.get("body", {}).get("data")
        if body_data:
            return base64.urlsafe_b64decode(body_data).decode("utf-8", errors="replace")
        parts = payload.get("parts", [])
        for part in parts:
            if part.get("mimeType") == "text/plain":
                data = part.get("body", {}).get("data", "")
                if data:
                    return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
        for part in parts:
            result = self._extract_body(part)
            if result:
                return result
        return ""

    def mark_processed(self, msg_id: str):
        label_id = self._get_or_create_label()
        requests.post(
            f"{GMAIL_API}/messages/{msg_id}/modify",
            headers=self._headers(),
            json={"addLabelIds": [label_id]},
        )

    def _get_or_create_label(self) -> str:
        if self._label_id_cache:
            return self._label_id_cache
        resp = requests.get(f"{GMAIL_API}/labels", headers=self._headers())
        labels = resp.json().get("labels", [])
        for label in labels:
            if label["name"] == "processed":
                self._label_id_cache = label["id"]
                return label["id"]
        resp = requests.post(
            f"{GMAIL_API}/labels",
            headers=self._headers(),
            json={"name": "processed", "labelListVisibility": "labelShow", "messageListVisibility": "show"},
        )
        label = resp.json()
        self._label_id_cache = label["id"]
        return label["id"]

    def build_message_link(self, msg_id: str) -> str:
        return f"https://mail.google.com/mail/u/0/#inbox/{msg_id}"
