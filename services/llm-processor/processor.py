import json
import re
import requests

EMPTY_RESULT = {"tasks": [], "events": [], "notes": []}


def build_extraction_prompt(subject: str, body: str, sender: str, date: str) -> str:
    return f"""Analyze this email and extract actionable items. Look for both explicit and implicit tasks, calendar events, and reference information worth saving.

**From:** {sender}
**Date:** {date}
**Subject:** {subject}

**Body:**
{body}

Respond ONLY with valid JSON in this exact format:
{{
  "tasks": [
    {{"title": "...", "description": "...", "due_date": "YYYY-MM-DD or empty string"}}
  ],
  "events": [
    {{"title": "...", "description": "...", "start": "ISO 8601 datetime", "end": "ISO 8601 datetime", "location": "or empty string"}}
  ],
  "notes": [
    {{"title": "...", "content": "...", "topic": "slug-format-topic"}}
  ]
}}

Rules:
- Extract tasks for any action items, requests, or implied obligations
- Extract events for any meetings, deadlines, or time-specific items
- Extract notes for reference information like credentials, links, summaries
- If nothing to extract for a category, use an empty array
- Infer implicit tasks (e.g., someone mentioning a problem implies you should look into it)
- Do NOT include the JSON in a markdown code block"""


class LLMProcessor:
    def __init__(self, ollama_url: str, model: str):
        self.ollama_url = ollama_url
        self.model = model

    def extract(self, subject: str, body: str, sender: str, date: str) -> dict:
        prompt = build_extraction_prompt(subject, body, sender, date)
        resp = requests.post(
            f"{self.ollama_url}/api/generate",
            json={"model": self.model, "prompt": prompt, "stream": False, "format": "json"},
            timeout=120,
        )
        if resp.status_code != 200:
            return dict(EMPTY_RESULT)
        raw = resp.json().get("response", "")
        return self._parse_response(raw)

    def _parse_response(self, raw: str) -> dict:
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.DOTALL)
        if match:
            candidate = match.group(1)
        else:
            candidate = raw
        candidate = candidate.strip()
        start = candidate.find("{")
        end = candidate.rfind("}")
        if start != -1 and end != -1:
            candidate = candidate[start:end + 1]
        try:
            parsed = json.loads(candidate)
            return {
                "tasks": parsed.get("tasks", []),
                "events": parsed.get("events", []),
                "notes": parsed.get("notes", []),
            }
        except json.JSONDecodeError:
            return dict(EMPTY_RESULT)
