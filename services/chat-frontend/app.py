import os
from flask import Flask, render_template, jsonify

app = Flask(__name__)

CHAT_BACKEND_URL = os.environ.get("CHAT_BACKEND_URL", "http://localhost:8088")


@app.route("/")
def index():
    return render_template("index.html", chat_backend_url=CHAT_BACKEND_URL)


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8089)
