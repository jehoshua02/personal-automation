import os
from flask import Flask, request, jsonify
from notes import NoteWriter

app = Flask(__name__)

NOTES_DIR = os.environ.get("NOTES_DIR", "/data/notes")
writer = NoteWriter(NOTES_DIR)


@app.route("/write", methods=["POST"])
def write():
    data = request.json
    if not data:
        return jsonify({"error": "request body required"}), 400
    path = writer.write_note(
        title=data.get("title", ""),
        content=data.get("content", ""),
        topic=data.get("topic", "general"),
        date=data.get("date", ""),
        email_link=data.get("email_link", ""),
    )
    return jsonify({"status": "ok", "path": path})


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8085)
