import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from chat import ChatClient

app = Flask(__name__)
CORS(app)

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://ollama:11434")
LLM_MODEL = os.environ.get("LLM_MODEL", "llama3.1:8b")
chat_client = ChatClient(OLLAMA_URL, LLM_MODEL)


@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    if not data or "message" not in data:
        return jsonify({"error": "message required"}), 400
    try:
        response = chat_client.send(data["message"])
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 502


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8088)
