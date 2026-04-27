import json
import re
import requests


def build_classification_prompt(subject: str, body: str, sender: str, date: str) -> str:
    return f"""Decide if this email is important enough to create tasks or calendar events from. Important emails contain action items, meeting requests, deadlines, or personally relevant information. Unimportant emails are newsletters, marketing, automated notifications, social media alerts, or bulk messages.

**From:** {sender}
**Date:** {date}
**Subject:** {subject}

**Body:**
{body}

Respond ONLY with valid JSON in this exact format:
{{
  "important": true or false,
  "reason": "one sentence explaining why"
}}"""


class EmailFilter:
    def __init__(self, ollama_url: str, model: str, whitelist: dict = None):
        self.ollama_url = ollama_url
        self.model = model
        self.whitelist = whitelist or {"senders": [], "domains": []}

    def _extract_email(self, sender: str) -> str:
        match = re.search(r"<(.+?)>", sender)
        return (match.group(1) if match else sender).lower()

    def check_whitelist(self, sender: str) -> bool:
        email = self._extract_email(sender)
        if email in [s.lower() for s in self.whitelist.get("senders", [])]:
            return True
        domain = email.split("@")[-1] if "@" in email else ""
        if domain in [d.lower() for d in self.whitelist.get("domains", [])]:
            return True
        return False

    def classify_with_llm(self, subject: str, body: str, sender: str, date: str) -> dict:
        prompt = build_classification_prompt(subject, body, sender, date)
        try:
            resp = requests.post(
                f"{self.ollama_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False, "format": "json"},
                timeout=120,
            )
        except requests.RequestException:
            return {"important": True, "reason": "LLM request failed, defaulting to important"}
        if resp.status_code != 200:
            return {"important": True, "reason": "LLM returned error, defaulting to important"}
        raw = resp.json().get("response", "")
        return self._parse_response(raw)

    def _parse_response(self, raw: str) -> dict:
        try:
            parsed = json.loads(raw.strip())
            return {
                "important": bool(parsed.get("important", True)),
                "reason": parsed.get("reason", ""),
            }
        except (json.JSONDecodeError, AttributeError):
            return {"important": True, "reason": "Could not parse LLM response, defaulting to important"}

    def filter(self, subject: str, body: str, sender: str, date: str) -> dict:
        if self.check_whitelist(sender):
            return {"important": True, "reason": "Sender is whitelisted", "method": "whitelist"}
        result = self.classify_with_llm(subject, body, sender, date)
        result["method"] = "llm"
        return result
