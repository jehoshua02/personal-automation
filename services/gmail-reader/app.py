import os
from flask import Flask, request, jsonify
from gmail import GmailClient

app = Flask(__name__)

AUTH_SERVICE_URL = os.environ.get("AUTH_SERVICE_URL", "http://auth:8080")
client = GmailClient(AUTH_SERVICE_URL)


@app.route("/fetch", methods=["POST"])
def fetch():
    max_results = request.json.get("max_results", 10) if request.json else 10
    messages = client.fetch_messages(max_results=max_results)
    return jsonify({"messages": messages})


@app.route("/mark-processed", methods=["POST"])
def mark_processed():
    msg_id = request.json.get("message_id") if request.json else None
    if not msg_id:
        return jsonify({"error": "message_id required"}), 400
    client.mark_processed(msg_id)
    return jsonify({"status": "ok"})


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081)
