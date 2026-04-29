import pytest
from unittest.mock import patch, MagicMock
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}


def test_chat_missing_body(client):
    resp = client.post("/chat", content_type="application/json")
    assert resp.status_code == 400


def test_chat_missing_message(client):
    resp = client.post("/chat", json={})
    assert resp.status_code == 400


@patch("app.chat_client")
def test_chat_success(mock_client, client):
    mock_client.send.return_value = "Hello from Ollama"
    resp = client.post("/chat", json={"message": "Hi"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["response"] == "Hello from Ollama"
    mock_client.send.assert_called_once_with("Hi")


@patch("app.chat_client")
def test_chat_ollama_error(mock_client, client):
    mock_client.send.side_effect = Exception("connection refused")
    resp = client.post("/chat", json={"message": "Hi"})
    assert resp.status_code == 502
    data = resp.get_json()
    assert "error" in data
