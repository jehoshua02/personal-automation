import pytest
from unittest.mock import patch, MagicMock
from tasks import TaskWriter


@pytest.fixture
def writer():
    return TaskWriter(auth_service_url="http://auth:8080", task_list_name="Auto-Extracted")


class TestGetToken:
    @patch("tasks.requests.get")
    def test_fetches_token(self, mock_get, writer):
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: {"access_token": "tok", "token_type": "Bearer"},
        )
        assert writer.get_token() == "tok"


class TestGetOrCreateTaskList:
    @patch("tasks.requests.post")
    @patch("tasks.requests.get")
    def test_returns_existing_list(self, mock_get, mock_post, writer):
        mock_get.side_effect = [
            MagicMock(status_code=200, json=lambda: {"access_token": "tok", "token_type": "Bearer"}),
            MagicMock(status_code=200, json=lambda: {
                "items": [{"id": "list1", "title": "Auto-Extracted"}]
            }),
        ]
        list_id = writer.get_or_create_task_list()
        assert list_id == "list1"
        mock_post.assert_not_called()

    @patch("tasks.requests.post")
    @patch("tasks.requests.get")
    def test_creates_list_if_missing(self, mock_get, mock_post, writer):
        mock_get.side_effect = [
            MagicMock(status_code=200, json=lambda: {"access_token": "tok", "token_type": "Bearer"}),
            MagicMock(status_code=200, json=lambda: {"items": []}),
            MagicMock(status_code=200, json=lambda: {"access_token": "tok", "token_type": "Bearer"}),
        ]
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {"id": "new_list", "title": "Auto-Extracted"},
        )
        list_id = writer.get_or_create_task_list()
        assert list_id == "new_list"


class TestWriteTask:
    @patch("tasks.requests.post")
    @patch("tasks.requests.get")
    def test_creates_task_in_list(self, mock_get, mock_post, writer):
        mock_get.side_effect = [
            MagicMock(status_code=200, json=lambda: {"access_token": "tok", "token_type": "Bearer"}),
            MagicMock(status_code=200, json=lambda: {
                "items": [{"id": "list1", "title": "Auto-Extracted"}]
            }),
            MagicMock(status_code=200, json=lambda: {"access_token": "tok", "token_type": "Bearer"}),
        ]
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {"id": "task1"},
        )
        result = writer.write_task(
            title="Review budget",
            description="Check the spreadsheet",
            due_date="2026-05-01",
            email_link="https://mail.google.com/mail/u/0/#inbox/msg1",
        )
        assert result["id"] == "task1"
        post_json = mock_post.call_args[1]["json"]
        assert post_json["title"] == "Review budget"
        assert "msg1" in post_json["notes"]

    @patch("tasks.requests.post")
    @patch("tasks.requests.get")
    def test_includes_due_date_when_provided(self, mock_get, mock_post, writer):
        mock_get.side_effect = [
            MagicMock(status_code=200, json=lambda: {"access_token": "tok", "token_type": "Bearer"}),
            MagicMock(status_code=200, json=lambda: {
                "items": [{"id": "list1", "title": "Auto-Extracted"}]
            }),
            MagicMock(status_code=200, json=lambda: {"access_token": "tok", "token_type": "Bearer"}),
        ]
        mock_post.return_value = MagicMock(status_code=200, json=lambda: {"id": "t1"})
        writer.write_task(title="T", description="D", due_date="2026-05-01", email_link="")
        post_json = mock_post.call_args[1]["json"]
        assert "2026-05-01" in post_json["due"]
