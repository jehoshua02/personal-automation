import json
import pytest
from unittest.mock import patch, MagicMock
from filter import EmailFilter, build_classification_prompt


@pytest.fixture
def whitelist():
    return {
        "senders": ["alice@example.com", "bob@work.com"],
        "domains": ["important.org"],
    }


@pytest.fixture
def filter_with_whitelist(whitelist):
    return EmailFilter(
        ollama_url="http://ollama:11434",
        model="llama3.1:8b",
        whitelist=whitelist,
    )


@pytest.fixture
def filter_empty_whitelist():
    return EmailFilter(
        ollama_url="http://ollama:11434",
        model="llama3.1:8b",
        whitelist={"senders": [], "domains": []},
    )


class TestWhitelist:
    def test_exact_sender_match(self, filter_with_whitelist):
        result = filter_with_whitelist.check_whitelist("alice@example.com")
        assert result is True

    def test_sender_match_case_insensitive(self, filter_with_whitelist):
        result = filter_with_whitelist.check_whitelist("Alice@Example.COM")
        assert result is True

    def test_domain_match(self, filter_with_whitelist):
        result = filter_with_whitelist.check_whitelist("anyone@important.org")
        assert result is True

    def test_domain_match_case_insensitive(self, filter_with_whitelist):
        result = filter_with_whitelist.check_whitelist("anyone@Important.ORG")
        assert result is True

    def test_no_match(self, filter_with_whitelist):
        result = filter_with_whitelist.check_whitelist("spam@junk.com")
        assert result is False

    def test_empty_whitelist(self, filter_empty_whitelist):
        result = filter_empty_whitelist.check_whitelist("alice@example.com")
        assert result is False

    def test_extracts_email_from_display_name(self, filter_with_whitelist):
        result = filter_with_whitelist.check_whitelist("Alice <alice@example.com>")
        assert result is True


class TestBuildClassificationPrompt:
    def test_includes_email_fields(self):
        prompt = build_classification_prompt(
            subject="Meeting tomorrow",
            body="Let's meet at 3pm",
            sender="alice@example.com",
            date="2026-04-27",
        )
        assert "Meeting tomorrow" in prompt
        assert "3pm" in prompt
        assert "alice@example.com" in prompt

    def test_requests_json_output(self):
        prompt = build_classification_prompt(
            subject="Test", body="Test", sender="a@b.com", date="2026-04-27"
        )
        assert "important" in prompt.lower()
        assert "JSON" in prompt


class TestLLMClassification:
    @patch("filter.requests.post")
    def test_important_email(self, mock_post, filter_empty_whitelist):
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {"response": json.dumps({"important": True, "reason": "Contains action item"})},
        )
        result = filter_empty_whitelist.classify_with_llm(
            subject="Urgent: review needed",
            body="Please review the PR by EOD",
            sender="boss@work.com",
            date="2026-04-27",
        )
        assert result["important"] is True
        assert result["reason"] == "Contains action item"

    @patch("filter.requests.post")
    def test_unimportant_email(self, mock_post, filter_empty_whitelist):
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {"response": json.dumps({"important": False, "reason": "Marketing newsletter"})},
        )
        result = filter_empty_whitelist.classify_with_llm(
            subject="Weekly deals!",
            body="Check out our sales",
            sender="noreply@store.com",
            date="2026-04-27",
        )
        assert result["important"] is False

    @patch("filter.requests.post")
    def test_unparseable_defaults_important(self, mock_post, filter_empty_whitelist):
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {"response": "not json at all"},
        )
        result = filter_empty_whitelist.classify_with_llm(
            subject="Test", body="Test", sender="a@b.com", date="2026-04-27"
        )
        assert result["important"] is True
        assert "parse" in result["reason"].lower()

    @patch("filter.requests.post")
    def test_ollama_error_defaults_important(self, mock_post, filter_empty_whitelist):
        mock_post.return_value = MagicMock(status_code=500)
        result = filter_empty_whitelist.classify_with_llm(
            subject="Test", body="Test", sender="a@b.com", date="2026-04-27"
        )
        assert result["important"] is True


class TestFilterEndToEnd:
    def test_whitelisted_skips_llm(self, filter_with_whitelist):
        with patch("filter.requests.post") as mock_post:
            result = filter_with_whitelist.filter(
                subject="Hi", body="Hello", sender="alice@example.com", date="2026-04-27"
            )
            mock_post.assert_not_called()
            assert result["important"] is True
            assert result["method"] == "whitelist"

    @patch("filter.requests.post")
    def test_non_whitelisted_calls_llm(self, mock_post, filter_with_whitelist):
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {"response": json.dumps({"important": False, "reason": "Spam"})},
        )
        result = filter_with_whitelist.filter(
            subject="Buy now", body="Great deals", sender="spam@junk.com", date="2026-04-27"
        )
        mock_post.assert_called_once()
        assert result["important"] is False
        assert result["method"] == "llm"
