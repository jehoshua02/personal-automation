import pytest
from unittest.mock import patch, MagicMock
from orchestrator import Pipeline


@pytest.fixture
def pipeline():
    return Pipeline(
        gmail_reader_url="http://gmail-reader:8081",
        llm_processor_url="http://llm-processor:8082",
        task_writer_url="http://task-writer:8083",
        calendar_writer_url="http://calendar-writer:8084",
        note_writer_url="http://note-writer:8085",
        email_filter_url="http://email-filter:8087",
    )


class TestFetchMessages:
    @patch("orchestrator.requests.post")
    def test_fetches_from_gmail_reader(self, mock_post, pipeline):
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {"messages": [{"id": "m1", "subject": "Test"}]},
        )
        messages = pipeline.fetch_messages(max_results=5)
        assert len(messages) == 1
        mock_post.assert_called_once_with(
            "http://gmail-reader:8081/fetch",
            json={"max_results": 5},
        )


class TestProcessMessage:
    @patch("orchestrator.requests.post")
    def test_sends_to_llm_processor(self, mock_post, pipeline):
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {"tasks": [], "events": [], "notes": []},
        )
        msg = {"subject": "Test", "body": "Hello", "from": "a@b.com", "date": "2026-04-27"}
        result = pipeline.process_message(msg)
        assert "tasks" in result
        call_json = mock_post.call_args[1]["json"]
        assert call_json["subject"] == "Test"


class TestRouteExtractions:
    @patch("orchestrator.requests.post")
    def test_routes_tasks(self, mock_post, pipeline):
        mock_post.return_value = MagicMock(status_code=200, json=lambda: {"id": "t1"})
        extractions = {
            "tasks": [{"title": "Do thing", "description": "Details", "due_date": ""}],
            "events": [],
            "notes": [],
        }
        results = pipeline.route_extractions(extractions, "https://mail.google.com/mail/u/0/#inbox/m1")
        assert len(results["tasks"]) == 1

    @patch("orchestrator.requests.post")
    def test_routes_events(self, mock_post, pipeline):
        mock_post.return_value = MagicMock(status_code=200, json=lambda: {"id": "e1"})
        extractions = {
            "tasks": [],
            "events": [{"title": "Meeting", "description": "", "start": "2026-04-28T15:00:00", "end": "2026-04-28T16:00:00", "location": ""}],
            "notes": [],
        }
        results = pipeline.route_extractions(extractions, "")
        assert len(results["events"]) == 1

    @patch("orchestrator.requests.post")
    def test_routes_notes(self, mock_post, pipeline):
        mock_post.return_value = MagicMock(status_code=200, json=lambda: {"status": "ok"})
        extractions = {
            "tasks": [],
            "events": [],
            "notes": [{"title": "Info", "content": "Key=123", "topic": "creds"}],
        }
        results = pipeline.route_extractions(extractions, "")
        assert len(results["notes"]) == 1


class TestMarkProcessed:
    @patch("orchestrator.requests.post")
    def test_marks_message_processed(self, mock_post, pipeline):
        mock_post.return_value = MagicMock(status_code=200)
        pipeline.mark_processed("msg1")
        mock_post.assert_called_once_with(
            "http://gmail-reader:8081/mark-processed",
            json={"message_id": "msg1", "label": "processed"},
        )


class TestFilterMessage:
    @patch("orchestrator.requests.post")
    def test_returns_filter_result(self, mock_post, pipeline):
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {"important": True, "reason": "Action item", "method": "llm"},
        )
        msg = {"subject": "Review", "body": "Please check", "from": "a@b.com", "date": "2026-04-27"}
        result = pipeline.filter_message(msg)
        assert result["important"] is True
        mock_post.assert_called_once_with(
            "http://email-filter:8087/filter",
            json={"subject": "Review", "body": "Please check", "from": "a@b.com", "date": "2026-04-27"},
        )

    @patch("orchestrator.requests.post")
    def test_defaults_important_on_error(self, mock_post, pipeline):
        mock_post.side_effect = Exception("connection refused")
        msg = {"subject": "Test", "body": "Body", "from": "a@b.com", "date": "2026-04-27"}
        result = pipeline.filter_message(msg)
        assert result["important"] is True


class TestRunPipeline:
    @patch("orchestrator.requests.post")
    def test_full_pipeline_flow(self, mock_post, pipeline):
        fetch_resp = MagicMock(status_code=200, json=lambda: {
            "messages": [{
                "id": "m1", "subject": "Review this", "body": "Please check",
                "from": "a@b.com", "date": "2026-04-27", "link": "https://mail.google.com/mail/u/0/#inbox/m1"
            }]
        })
        filter_resp = MagicMock(status_code=200, json=lambda: {
            "important": True, "reason": "Action item", "method": "llm",
        })
        extract_resp = MagicMock(status_code=200, json=lambda: {
            "tasks": [{"title": "Review", "description": "Check it", "due_date": ""}],
            "events": [], "notes": [],
        })
        write_resp = MagicMock(status_code=200, json=lambda: {"id": "t1"})
        mark_resp = MagicMock(status_code=200, json=lambda: {"status": "ok"})
        mock_post.side_effect = [fetch_resp, filter_resp, extract_resp, write_resp, mark_resp]
        results = pipeline.run(max_results=1)
        assert len(results) == 1
        assert results[0]["extractions"]["tasks"][0]["title"] == "Review"
        assert mock_post.call_count == 5

    @patch("orchestrator.requests.post")
    def test_skips_filtered_email(self, mock_post, pipeline):
        fetch_resp = MagicMock(status_code=200, json=lambda: {
            "messages": [{
                "id": "m1", "subject": "Weekly deals!", "body": "Buy now",
                "from": "spam@store.com", "date": "2026-04-27", "link": ""
            }]
        })
        filter_resp = MagicMock(status_code=200, json=lambda: {
            "important": False, "reason": "Marketing", "method": "llm",
        })
        mark_resp = MagicMock(status_code=200, json=lambda: {"status": "ok"})
        mock_post.side_effect = [fetch_resp, filter_resp, mark_resp]
        results = pipeline.run(max_results=1)
        assert len(results) == 1
        assert results[0]["filtered"] is True
        assert results[0]["filter_reason"] == "Marketing"
        assert "extractions" not in results[0]
        assert mock_post.call_count == 3
        mark_call = mock_post.call_args_list[2]
        assert mark_call[1]["json"]["label"] == "AutoFiltered"

    @patch("orchestrator.requests.post")
    def test_handles_empty_inbox(self, mock_post, pipeline):
        mock_post.return_value = MagicMock(
            status_code=200, json=lambda: {"messages": []}
        )
        results = pipeline.run()
        assert results == []
