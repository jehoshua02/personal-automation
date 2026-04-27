import json
import os
from flask import Flask, request, jsonify
from filter import EmailFilter

app = Flask(__name__)

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://ollama:11434")
LLM_MODEL = os.environ.get("LLM_MODEL", "llama3.1:8b")
WHITELIST_PATH = os.environ.get("WHITELIST_PATH", "/config/whitelist.json")


def load_whitelist(path: str) -> dict:
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"senders": [], "domains": []}


email_filter = EmailFilter(OLLAMA_URL, LLM_MODEL)


@app.route("/filter", methods=["POST"])
def filter_email():
    data = request.json
    if not data:
        return jsonify({"error": "request body required"}), 400
    email_filter.whitelist = load_whitelist(WHITELIST_PATH)
    result = email_filter.filter(
        subject=data.get("subject", ""),
        body=data.get("body", ""),
        sender=data.get("from", ""),
        date=data.get("date", ""),
    )
    return jsonify(result)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8087)
