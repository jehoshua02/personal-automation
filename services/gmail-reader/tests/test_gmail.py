import json
import pytest
from unittest.mock import patch, MagicMock
from gmail import GmailClient


@pytest.fixture
def gmail_client():
    return GmailClient(auth_service_url="http://auth:8080")


class TestGetToken:
    @patch("gmail.requests.get")
    def test_fetches_token_from_auth_service(self, mock_get, gmail_client):
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: {"access_token": "tok123", "token_type": "Bearer"},
        )
        token = gmail_client.get_token()
        assert token == "tok123"
        mock_get.assert_called_once_with("http://auth:8080/token")

    @patch("gmail.requests.get")
    def test_raises_on_auth_failure(self, mock_get, gmail_client):
        mock_get.return_value = MagicMock(status_code=401)
        with pytest.raises(Exception):
            gmail_client.get_token()


class TestFetchMessages:
    @patch("gmail.requests.get")
    def test_returns_parsed_messages(self, mock_get, gmail_client):
        token_resp = MagicMock(status_code=200, json=lambda: {"access_token": "tok", "token_type": "Bearer"})
        list_resp = MagicMock(
            status_code=200,
            json=lambda: {"messages": [{"id": "msg1"}]},
        )
        msg_resp = MagicMock(
            status_code=200,
            json=lambda: {
                "id": "msg1",
                "threadId": "t1",
                "payload": {
                    "headers": [
                        {"name": "From", "value": "alice@example.com"},
                        {"name": "To", "value": "bob@example.com"},
                        {"name": "Subject", "value": "Hello"},
                        {"name": "Date", "value": "Mon, 27 Apr 2026 10:00:00 +0000"},
                    ],
                    "body": {"data": "SGVsbG8gV29ybGQ="},
                },
            },
        )
        mock_get.side_effect = [token_resp, list_resp, token_resp, msg_resp]
        messages = gmail_client.fetch_messages(max_results=1)
        assert len(messages) == 1
        assert messages[0]["id"] == "msg1"
        assert messages[0]["from"] == "alice@example.com"
        assert messages[0]["subject"] == "Hello"
        assert "Hello World" in messages[0]["body"]

    @patch("gmail.requests.get")
    def test_excludes_processed_label(self, mock_get, gmail_client):
        mock_get.side_effect = [
            MagicMock(status_code=200, json=lambda: {"access_token": "tok", "token_type": "Bearer"}),
            MagicMock(status_code=200, json=lambda: {"messages": []}),
        ]
        gmail_client.fetch_messages()
        call_args = mock_get.call_args_list[1]
        params = call_args[1].get("params", {})
        assert "-label:processed" in params.get("q", "")

    @patch("gmail.requests.get")
    def test_handles_empty_inbox(self, mock_get, gmail_client):
        mock_get.side_effect = [
            MagicMock(status_code=200, json=lambda: {"access_token": "tok", "token_type": "Bearer"}),
            MagicMock(status_code=200, json=lambda: {}),
        ]
        messages = gmail_client.fetch_messages()
        assert messages == []


class TestMarkProcessed:
    @patch("gmail.requests.post")
    @patch("gmail.requests.get")
    def test_applies_processed_label(self, mock_get, mock_post, gmail_client):
        token_resp = MagicMock(status_code=200, json=lambda: {"access_token": "tok", "token_type": "Bearer"})
        mock_get.side_effect = [
            token_resp,
            MagicMock(status_code=200, json=lambda: {"labels": [{"id": "Label_1", "name": "processed"}]}),
            token_resp,
        ]
        mock_post.return_value = MagicMock(status_code=200)
        gmail_client.mark_processed("msg1")
        post_call = mock_post.call_args
        body = post_call[1].get("json", {})
        assert "Label_1" in body.get("addLabelIds", [])

    @patch("gmail.requests.post")
    @patch("gmail.requests.get")
    def test_creates_label_if_missing(self, mock_get, mock_post, gmail_client):
        token_resp = MagicMock(status_code=200, json=lambda: {"access_token": "tok", "token_type": "Bearer"})
        mock_get.side_effect = [
            token_resp,
            MagicMock(status_code=200, json=lambda: {"labels": []}),
            token_resp,
            token_resp,
        ]
        mock_post.side_effect = [
            MagicMock(status_code=200, json=lambda: {"id": "Label_new", "name": "processed"}),
            MagicMock(status_code=200),
        ]
        gmail_client.mark_processed("msg1")
        create_call = mock_post.call_args_list[0]
        assert create_call[1]["json"]["name"] == "processed"


class TestBuildMessageLink:
    def test_returns_gmail_link(self, gmail_client):
        link = gmail_client.build_message_link("msg123")
        assert "msg123" in link
        assert "mail.google.com" in link
