import os
from flask import Flask, request, jsonify
from processor import LLMProcessor

app = Flask(__name__)

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://ollama:11434")
LLM_MODEL = os.environ.get("LLM_MODEL", "llama3.1:8b")
processor = LLMProcessor(OLLAMA_URL, LLM_MODEL)


@app.route("/extract", methods=["POST"])
def extract():
    data = request.json
    if not data:
        return jsonify({"error": "request body required"}), 400
    result = processor.extract(
        subject=data.get("subject", ""),
        body=data.get("body", ""),
        sender=data.get("from", ""),
        date=data.get("date", ""),
    )
    return jsonify(result)


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8082)
