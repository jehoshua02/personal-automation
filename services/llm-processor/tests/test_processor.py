import json
import pytest
from unittest.mock import patch, MagicMock
from processor import LLMProcessor, build_extraction_prompt


@pytest.fixture
def processor():
    return LLMProcessor(ollama_url="http://ollama:11434", model="llama3.1:8b")


class TestBuildExtractionPrompt:
    def test_includes_subject(self):
        prompt = build_extraction_prompt(
            subject="Meeting tomorrow",
            body="Let's meet at 3pm",
            sender="alice@example.com",
            date="2026-04-27",
        )
        assert "Meeting tomorrow" in prompt

    def test_includes_body(self):
        prompt = build_extraction_prompt(
            subject="Test",
            body="Please review the budget spreadsheet",
            sender="alice@example.com",
            date="2026-04-27",
        )
        assert "review the budget spreadsheet" in prompt

    def test_requests_json_output(self):
        prompt = build_extraction_prompt(
            subject="Test", body="Test", sender="a@b.com", date="2026-04-27"
        )
        assert "JSON" in prompt


class TestExtract:
    @patch("processor.requests.post")
    def test_parses_valid_llm_response(self, mock_post, processor):
        llm_response = json.dumps({
            "tasks": [{"title": "Review budget", "description": "Check the spreadsheet", "due_date": ""}],
            "events": [],
            "notes": [],
        })
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {"response": llm_response},
        )
        result = processor.extract(
            subject="Budget review",
            body="Can you review the budget spreadsheet?",
            sender="alice@example.com",
            date="2026-04-27",
        )
        assert len(result["tasks"]) == 1
        assert result["tasks"][0]["title"] == "Review budget"
        assert result["events"] == []
        assert result["notes"] == []

    @patch("processor.requests.post")
    def test_handles_llm_returning_json_in_markdown(self, mock_post, processor):
        llm_response = '```json\n{"tasks": [], "events": [{"title": "Meeting", "description": "", "start": "2026-04-28T15:00:00", "end": "2026-04-28T16:00:00", "location": ""}], "notes": []}\n```'
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {"response": llm_response},
        )
        result = processor.extract(
            subject="Meeting", body="Meet at 3pm tomorrow", sender="a@b.com", date="2026-04-27"
        )
        assert len(result["events"]) == 1
        assert result["events"][0]["title"] == "Meeting"

    @patch("processor.requests.post")
    def test_returns_empty_on_unparseable_response(self, mock_post, processor):
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {"response": "I don't understand this email"},
        )
        result = processor.extract(
            subject="Test", body="Random noise", sender="a@b.com", date="2026-04-27"
        )
        assert result["tasks"] == []
        assert result["events"] == []
        assert result["notes"] == []

    @patch("processor.requests.post")
    def test_sends_to_correct_model(self, mock_post, processor):
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {"response": '{"tasks":[],"events":[],"notes":[]}'},
        )
        processor.extract(subject="T", body="B", sender="a@b.com", date="2026-04-27")
        call_json = mock_post.call_args[1]["json"]
        assert call_json["model"] == "llama3.1:8b"
