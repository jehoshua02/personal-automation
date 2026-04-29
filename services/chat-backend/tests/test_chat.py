import pytest
from unittest.mock import patch, MagicMock
from chat import ChatClient


@patch("chat.requests.post")
def test_send_success(mock_post):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"response": "I am Ollama"}
    mock_post.return_value = mock_resp

    client = ChatClient("http://ollama:11434", "llama3.1:8b")
    result = client.send("Hello")

    assert result == "I am Ollama"
    mock_post.assert_called_once_with(
        "http://ollama:11434/api/generate",
        json={"model": "llama3.1:8b", "prompt": "Hello", "stream": False},
        timeout=120,
    )


@patch("chat.requests.post")
def test_send_ollama_non_200(mock_post):
    mock_resp = MagicMock()
    mock_resp.status_code = 500
    mock_resp.raise_for_status.side_effect = Exception("500 Server Error")
    mock_post.return_value = mock_resp

    client = ChatClient("http://ollama:11434", "llama3.1:8b")
    with pytest.raises(Exception):
        client.send("Hello")
