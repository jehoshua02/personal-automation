import os
from flask import Flask, request, jsonify
from tasks import TaskWriter

app = Flask(__name__)

AUTH_SERVICE_URL = os.environ.get("AUTH_SERVICE_URL", "http://auth:8080")
writer = TaskWriter(AUTH_SERVICE_URL)


@app.route("/write", methods=["POST"])
def write():
    data = request.json
    if not data:
        return jsonify({"error": "request body required"}), 400
    result = writer.write_task(
        title=data.get("title", ""),
        description=data.get("description", ""),
        due_date=data.get("due_date", ""),
        email_link=data.get("email_link", ""),
    )
    return jsonify(result)


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8083)
