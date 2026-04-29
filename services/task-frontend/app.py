import os
from flask import Flask, render_template, jsonify

app = Flask(__name__)

TASK_SERVICE_URL = os.environ.get("TASK_SERVICE_URL", "http://localhost:8090")


@app.route("/")
def index():
    return render_template("index.html", task_service_url=TASK_SERVICE_URL)


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8091)
