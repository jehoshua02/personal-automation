"""
Integration and UAT tests for the gmail-processing-pipeline.

Prerequisites:
  - All services running: docker compose up -d
  - OAuth tokens valid (run auth flow if expired)
  - Ollama model pulled: docker compose exec ollama ollama pull llama3.1:8b

Run:
  docker compose run --rm e2e-tests
"""

import base64
import json
import time
import pytest
import requests

AUTH_URL = "http://auth:8080"
GMAIL_READER_URL = "http://gmail-reader:8081"
LLM_PROCESSOR_URL = "http://llm-processor:8082"
TASK_WRITER_URL = "http://task-writer:8083"
CALENDAR_WRITER_URL = "http://calendar-writer:8084"
NOTE_WRITER_URL = "http://note-writer:8085"
EMAIL_FILTER_URL = "http://email-filter:8087"
ORCHESTRATOR_URL = "http://orchestrator:8086"
GMAIL_API = "https://gmail.googleapis.com/gmail/v1/users/me"


def get_token():
    resp = requests.get(f"{AUTH_URL}/token")
    assert resp.status_code == 200, f"Auth service not authenticated: {resp.text}"
    return resp.json()["access_token"]


def gmail_headers():
    return {"Authorization": f"Bearer {get_token()}"}


def insert_test_email(subject, body, sender="e2e-test@example.com"):
    raw = f"From: {sender}\r\nTo: jehoshua02dev@gmail.com\r\nSubject: {subject}\r\nDate: Mon, 27 Apr 2026 10:00:00 +0000\r\nContent-Type: text/plain\r\n\r\n{body}"
    encoded = base64.urlsafe_b64encode(raw.encode()).decode().rstrip("=")
    resp = requests.post(
        f"{GMAIL_API}/messages",
        headers=gmail_headers(),
        json={"raw": encoded},
    )
    assert resp.status_code == 200, f"Failed to insert email: {resp.text}"
    return resp.json()["id"]


def delete_test_email(msg_id):
    requests.delete(f"{GMAIL_API}/messages/{msg_id}", headers=gmail_headers())


def remove_processed_label(msg_id):
    resp = requests.get(f"{GMAIL_API}/labels", headers=gmail_headers())
    labels = resp.json().get("labels", [])
    for label in labels:
        if label["name"] == "processed":
            requests.post(
                f"{GMAIL_API}/messages/{msg_id}/modify",
                headers=gmail_headers(),
                json={"removeLabelIds": [label["id"]]},
            )
            return


class TestServiceHealth:
    """Verify all services are running and responsive."""

    @pytest.mark.parametrize("url,name", [
        (AUTH_URL, "auth"),
        (GMAIL_READER_URL, "gmail-reader"),
        (LLM_PROCESSOR_URL, "llm-processor"),
        (TASK_WRITER_URL, "task-writer"),
        (CALENDAR_WRITER_URL, "calendar-writer"),
        (NOTE_WRITER_URL, "note-writer"),
        (EMAIL_FILTER_URL, "email-filter"),
        (ORCHESTRATOR_URL, "orchestrator"),
    ])
    def test_health(self, url, name):
        resp = requests.get(f"{url}/health")
        assert resp.status_code == 200, f"{name} health check failed"
        assert resp.json()["status"] == "ok"


class TestAuthIntegration:
    """Verify OAuth tokens work against Google APIs."""

    def test_token_endpoint_returns_token(self):
        resp = requests.get(f"{AUTH_URL}/token")
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data

    def test_token_works_against_gmail(self):
        resp = requests.get(f"{GMAIL_API}/profile", headers=gmail_headers())
        assert resp.status_code == 200
        assert resp.json()["emailAddress"] == "jehoshua02dev@gmail.com"

    def test_token_works_against_tasks(self):
        resp = requests.get(
            "https://tasks.googleapis.com/tasks/v1/users/@me/lists",
            headers=gmail_headers(),
        )
        assert resp.status_code == 200

    def test_token_works_against_calendar(self):
        resp = requests.get(
            "https://www.googleapis.com/calendar/v3/calendars/primary/events",
            headers=gmail_headers(),
            params={"maxResults": 1},
        )
        assert resp.status_code == 200


class TestGmailReaderIntegration:
    """Verify gmail-reader fetches real messages."""

    def test_fetch_returns_messages_list(self):
        resp = requests.post(f"{GMAIL_READER_URL}/fetch", json={"max_results": 1})
        assert resp.status_code == 200
        assert "messages" in resp.json()

    def test_fetched_message_has_required_fields(self):
        msg_id = insert_test_email("E2E field check", "Test body")
        try:
            resp = requests.post(f"{GMAIL_READER_URL}/fetch", json={"max_results": 10})
            messages = resp.json()["messages"]
            matching = [m for m in messages if m["id"] == msg_id]
            assert len(matching) == 1, "Inserted email not found"
            msg = matching[0]
            for field in ["id", "subject", "from", "to", "date", "body", "link"]:
                assert field in msg, f"Missing field: {field}"
            assert "mail.google.com" in msg["link"]
        finally:
            remove_processed_label(msg_id)
            delete_test_email(msg_id)


class TestLLMProcessorIntegration:
    """Verify LLM extracts structured data from email content."""

    def test_extracts_task(self):
        """LLM is non-deterministic. Retry up to 3 times."""
        payload = {
            "subject": "Urgent: expense report due Friday",
            "body": "Hi,\n\nPlease submit your Q3 expense report by this Friday end of day.\nAttach all receipts. Also update the shared budget tracker spreadsheet.\n\nThanks,\nYour Manager",
            "from": "boss@company.com",
            "date": "2026-04-27",
        }
        for attempt in range(3):
            resp = requests.post(f"{LLM_PROCESSOR_URL}/extract", json=payload)
            assert resp.status_code == 200
            data = resp.json()
            assert "tasks" in data
            assert "events" in data
            assert "notes" in data
            total = len(data["tasks"]) + len(data["events"]) + len(data["notes"])
            if total > 0:
                return
        pytest.fail(f"LLM extracted nothing after 3 attempts: {data}")

    def test_extracts_event(self):
        """LLM is non-deterministic. Retry up to 3 times."""
        payload = {
            "subject": "Meeting: Q3 planning session Wednesday 2pm",
            "body": "Hi team,\n\nWe have a Q3 planning session scheduled for Wednesday April 29 at 2:00 PM in Conference Room A.\nPlease bring your department projections.\nThe meeting will last approximately 2 hours.\n\nBest,\nDirector",
            "from": "director@company.com",
            "date": "2026-04-27",
        }
        for attempt in range(3):
            resp = requests.post(f"{LLM_PROCESSOR_URL}/extract", json=payload)
            data = resp.json()
            total = len(data["tasks"]) + len(data["events"]) + len(data["notes"])
            if total > 0:
                return
        pytest.fail(f"LLM extracted nothing after 3 attempts: {data}")

    def test_returns_valid_structure_on_empty_email(self):
        resp = requests.post(f"{LLM_PROCESSOR_URL}/extract", json={
            "subject": "", "body": "", "from": "", "date": "",
        })
        data = resp.json()
        assert isinstance(data["tasks"], list)
        assert isinstance(data["events"], list)
        assert isinstance(data["notes"], list)


class TestTaskWriterIntegration:
    """Verify tasks are written to Google Tasks."""

    def test_creates_task(self):
        resp = requests.post(f"{TASK_WRITER_URL}/write", json={
            "title": "E2E test task",
            "description": "Created by e2e test",
            "due_date": "",
            "email_link": "https://mail.google.com/mail/u/0/#inbox/test",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "id" in data, f"Task not created: {data}"
        assert data["title"] == "E2E test task"


class TestCalendarWriterIntegration:
    """Verify events are written to Google Calendar."""

    def test_creates_event(self):
        resp = requests.post(f"{CALENDAR_WRITER_URL}/write", json={
            "title": "E2E test event",
            "description": "Created by e2e test",
            "start": "2026-12-25T10:00:00",
            "end": "2026-12-25T11:00:00",
            "location": "Test Room",
            "email_link": "",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "id" in data, f"Event not created: {data}"

    def test_defaults_end_time(self):
        resp = requests.post(f"{CALENDAR_WRITER_URL}/write", json={
            "title": "E2E no-end event",
            "description": "",
            "start": "2026-12-25T14:00:00",
            "end": "",
            "location": "",
            "email_link": "",
        })
        data = resp.json()
        assert "id" in data, f"Event with default end not created: {data}"


class TestNoteWriterIntegration:
    """Verify notes are written to disk."""

    def test_creates_note(self):
        resp = requests.post(f"{NOTE_WRITER_URL}/write", json={
            "title": "E2E test note",
            "content": "Some reference info",
            "topic": "e2e-test",
            "date": "2026-04-27",
            "email_link": "https://mail.google.com/mail/u/0/#inbox/test",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert "2026-04-27" in data["path"]
        assert "e2e-test" in data["path"]


class TestEmailFilterIntegration:
    """Verify email-filter classifies emails via LLM."""

    def test_filters_spam(self):
        """LLM is non-deterministic. Retry up to 3 times."""
        payload = {
            "subject": "🔥 HUGE SALE 80% OFF Everything!!!",
            "body": "Don't miss our biggest sale of the year! Use code SAVE80 at checkout. "
                    "Free shipping on orders over $25. Unsubscribe here.",
            "from": "noreply@deals-store-promo.com",
            "date": "2026-04-27",
        }
        for attempt in range(3):
            resp = requests.post(f"{EMAIL_FILTER_URL}/filter", json=payload)
            assert resp.status_code == 200
            data = resp.json()
            assert "important" in data
            assert "reason" in data
            assert "method" in data
            if data["important"] is False:
                return
        pytest.fail(f"Filter did not reject obvious spam after 3 attempts: {data}")

    def test_passes_important_email(self):
        """LLM is non-deterministic. Retry up to 3 times."""
        payload = {
            "subject": "Action required: sign the contract by Friday",
            "body": "Hi,\n\nThe client contract is ready for your signature. "
                    "Please review and sign by end of day Friday.\n\nThanks,\nLegal",
            "from": "legal@company.com",
            "date": "2026-04-27",
        }
        for attempt in range(3):
            resp = requests.post(f"{EMAIL_FILTER_URL}/filter", json=payload)
            data = resp.json()
            if data["important"] is True:
                return
        pytest.fail(f"Filter rejected important email after 3 attempts: {data}")


class TestFullPipeline:
    """End-to-end: insert email, run pipeline, verify outputs."""

    def test_pipeline_processes_email(self):
        """Full pipeline: insert email, process, verify outputs. Retry LLM up to 3 times."""
        for attempt in range(3):
            msg_id = insert_test_email(
                subject="E2E: Lunch with client Wednesday noon",
                body="Reminder: lunch with the client on Wednesday at noon at Olive Garden.\n"
                     "Bring the signed contract.\n"
                     "Client phone: 555-0142.",
            )
            try:
                resp = requests.post(f"{ORCHESTRATOR_URL}/run", json={"max_results": 10})
                assert resp.status_code == 200
                data = resp.json()
                assert data["count"] >= 1

                result = None
                for r in data["results"]:
                    if r["message_id"] == msg_id:
                        result = r
                        break
                assert result is not None, "Pipeline did not process the test email"

                if result.get("filtered"):
                    delete_test_email(msg_id)
                    continue

                ex = result["extractions"]
                total = len(ex["tasks"]) + len(ex["events"]) + len(ex["notes"])
                if total == 0:
                    delete_test_email(msg_id)
                    continue

                wr = result["write_results"]
                for task in wr["tasks"]:
                    assert "id" in task, f"Task write failed: {task}"
                for event in wr["events"]:
                    assert "id" in event, f"Event write failed: {event}"
                for note in wr["notes"]:
                    assert note.get("status") == "ok", f"Note write failed: {note}"
                return
            finally:
                delete_test_email(msg_id)
        pytest.fail("Pipeline produced no extractions after 3 attempts")

    def test_pipeline_filters_spam(self):
        """Pipeline should filter obvious spam and label it AutoFiltered."""
        for attempt in range(3):
            msg_id = insert_test_email(
                subject="You won a FREE iPhone!!! Click NOW",
                body="Congratulations! You have been selected to receive a free iPhone 15! "
                     "Click the link below to claim your prize. Offer expires in 24 hours! "
                     "No purchase necessary. Unsubscribe: reply STOP.",
                sender="deals@win-free-prizes-now.com",
            )
            try:
                resp = requests.post(f"{ORCHESTRATOR_URL}/run", json={"max_results": 10})
                data = resp.json()
                result = None
                for r in data["results"]:
                    if r["message_id"] == msg_id:
                        result = r
                        break
                assert result is not None, "Pipeline did not process the test email"
                if result.get("filtered"):
                    resp = requests.get(
                        f"{GMAIL_API}/messages/{msg_id}",
                        headers=gmail_headers(),
                    )
                    label_ids = resp.json().get("labelIds", [])
                    resp = requests.get(f"{GMAIL_API}/labels", headers=gmail_headers())
                    labels = {l["id"]: l["name"] for l in resp.json().get("labels", [])}
                    applied = [labels.get(lid, "") for lid in label_ids]
                    assert "AutoFiltered" in applied, f"AutoFiltered label not applied: {applied}"
                    return
            finally:
                delete_test_email(msg_id)
        pytest.fail("Pipeline did not filter obvious spam after 3 attempts")

    def test_processed_emails_not_refetched(self):
        resp = requests.post(f"{ORCHESTRATOR_URL}/run", json={"max_results": 10})
        pre_count = resp.json()["count"]

        msg_id = insert_test_email("E2E: already processed test", "Nothing here")
        try:
            requests.post(f"{ORCHESTRATOR_URL}/run", json={"max_results": 10})

            resp = requests.post(f"{ORCHESTRATOR_URL}/run", json={"max_results": 10})
            data = resp.json()
            processed_ids = [r["message_id"] for r in data["results"]]
            assert msg_id not in processed_ids, "Already-processed email was re-processed"
        finally:
            delete_test_email(msg_id)
