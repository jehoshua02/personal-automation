import pytest
from unittest.mock import patch, MagicMock
from calendar_writer import CalendarWriter


@pytest.fixture
def writer():
    return CalendarWriter(auth_service_url="http://auth:8080")


class TestGetToken:
    @patch("calendar_writer.requests.get")
    def test_fetches_token(self, mock_get, writer):
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: {"access_token": "tok", "token_type": "Bearer"},
        )
        assert writer.get_token() == "tok"


class TestWriteEvent:
    @patch("calendar_writer.requests.post")
    @patch("calendar_writer.requests.get")
    def test_creates_event(self, mock_get, mock_post, writer):
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: {"access_token": "tok", "token_type": "Bearer"},
        )
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {"id": "evt1", "summary": "Meeting"},
        )
        result = writer.write_event(
            title="Meeting",
            description="Team sync",
            start="2026-04-28T15:00:00",
            end="2026-04-28T16:00:00",
            location="Room 3",
            email_link="https://mail.google.com/mail/u/0/#inbox/msg1",
        )
        assert result["id"] == "evt1"

    @patch("calendar_writer.requests.post")
    @patch("calendar_writer.requests.get")
    def test_uses_calendar_id_env_var(self, mock_get, mock_post):
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: {"access_token": "tok", "token_type": "Bearer"},
        )
        mock_post.return_value = MagicMock(status_code=200, json=lambda: {"id": "e1"})
        w = CalendarWriter(auth_service_url="http://auth:8080", calendar_id="abc123")
        w.write_event(
            title="T", description="D", start="2026-04-28T15:00:00",
            end="2026-04-28T16:00:00", location="", email_link="",
        )
        url = mock_post.call_args[0][0]
        assert "/calendars/abc123/events" in url

    @patch("calendar_writer.requests.post")
    @patch("calendar_writer.requests.get")
    def test_defaults_to_primary_calendar(self, mock_get, mock_post, writer):
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: {"access_token": "tok", "token_type": "Bearer"},
        )
        mock_post.return_value = MagicMock(status_code=200, json=lambda: {"id": "e1"})
        writer.write_event(
            title="T", description="D", start="2026-04-28T15:00:00",
            end="2026-04-28T16:00:00", location="", email_link="",
        )
        url = mock_post.call_args[0][0]
        assert "/calendars/primary/events" in url

    @patch("calendar_writer.requests.post")
    @patch("calendar_writer.requests.get")
    def test_includes_email_link_in_description(self, mock_get, mock_post, writer):
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: {"access_token": "tok", "token_type": "Bearer"},
        )
        mock_post.return_value = MagicMock(status_code=200, json=lambda: {"id": "e1"})
        writer.write_event(
            title="T", description="D", start="2026-04-28T15:00:00",
            end="2026-04-28T16:00:00", location="",
            email_link="https://mail.google.com/mail/u/0/#inbox/msg1",
        )
        post_json = mock_post.call_args[1]["json"]
        assert "msg1" in post_json["description"]

    @patch("calendar_writer.requests.post")
    @patch("calendar_writer.requests.get")
    def test_defaults_end_to_start_plus_one_hour(self, mock_get, mock_post, writer):
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: {"access_token": "tok", "token_type": "Bearer"},
        )
        mock_post.return_value = MagicMock(status_code=200, json=lambda: {"id": "e1"})
        writer.write_event(
            title="T", description="D", start="2026-04-28T15:00:00",
            end="", location="", email_link="",
        )
        post_json = mock_post.call_args[1]["json"]
        assert post_json["end"]["dateTime"] == "2026-04-28T16:00:00"

    @patch("calendar_writer.requests.post")
    @patch("calendar_writer.requests.get")
    def test_sets_location(self, mock_get, mock_post, writer):
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: {"access_token": "tok", "token_type": "Bearer"},
        )
        mock_post.return_value = MagicMock(status_code=200, json=lambda: {"id": "e1"})
        writer.write_event(
            title="T", description="D", start="2026-04-28T15:00:00",
            end="2026-04-28T16:00:00", location="Coffee Shop",
            email_link="",
        )
        post_json = mock_post.call_args[1]["json"]
        assert post_json["location"] == "Coffee Shop"
