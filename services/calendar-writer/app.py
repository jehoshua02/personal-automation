import os
from flask import Flask, request, jsonify
from calendar_writer import CalendarWriter

app = Flask(__name__)

AUTH_SERVICE_URL = os.environ.get("AUTH_SERVICE_URL", "http://auth:8080")
CALENDAR_ID = os.environ.get("CALENDAR_ID", "primary")
writer = CalendarWriter(AUTH_SERVICE_URL, calendar_id=CALENDAR_ID)


@app.route("/write", methods=["POST"])
def write():
    data = request.json
    if not data:
        return jsonify({"error": "request body required"}), 400
    result = writer.write_event(
        title=data.get("title", ""),
        description=data.get("description", ""),
        start=data.get("start", ""),
        end=data.get("end", ""),
        location=data.get("location", ""),
        email_link=data.get("email_link", ""),
    )
    return jsonify(result)


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8084)
