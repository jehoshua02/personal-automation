import requests


class ChatClient:
    def __init__(self, ollama_url: str, model: str):
        self.ollama_url = ollama_url
        self.model = model

    def send(self, message: str) -> str:
        resp = requests.post(
            f"{self.ollama_url}/api/generate",
            json={"model": self.model, "prompt": message, "stream": False},
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json().get("response", "")
