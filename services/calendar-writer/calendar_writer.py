from datetime import datetime, timedelta
import requests

CALENDAR_API = "https://www.googleapis.com/calendar/v3"


class CalendarWriter:
    def __init__(self, auth_service_url: str, calendar_id: str = "primary"):
        self.auth_service_url = auth_service_url
        self.calendar_id = calendar_id

    def get_token(self) -> str:
        resp = requests.get(f"{self.auth_service_url}/token")
        if resp.status_code != 200:
            raise Exception(f"Auth service returned {resp.status_code}")
        return resp.json()["access_token"]

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self.get_token()}"}

    def write_event(self, title: str, description: str, start: str, end: str, location: str, email_link: str) -> dict:
        full_description = description
        if email_link:
            full_description += f"\n\nSource: {email_link}"
        if not end and start:
            end = self._default_end(start)
        body = {
            "summary": title,
            "description": full_description,
            "start": {"dateTime": start, "timeZone": "America/Los_Angeles"},
            "end": {"dateTime": end, "timeZone": "America/Los_Angeles"},
        }
        if location:
            body["location"] = location
        resp = requests.post(
            f"{CALENDAR_API}/calendars/{self.calendar_id}/events",
            headers=self._headers(),
            json=body,
        )
        return resp.json()

    def _default_end(self, start: str) -> str:
        for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S"):
            try:
                dt = datetime.strptime(start, fmt)
                return (dt + timedelta(hours=1)).strftime(fmt)
            except ValueError:
                continue
        return start
