import os
from flask import Flask, request, jsonify
from orchestrator import Pipeline

app = Flask(__name__)

pipeline = Pipeline(
    gmail_reader_url=os.environ.get("GMAIL_READER_URL", "http://gmail-reader:8081"),
    llm_processor_url=os.environ.get("LLM_PROCESSOR_URL", "http://llm-processor:8082"),
    task_writer_url=os.environ.get("TASK_WRITER_URL", "http://task-writer:8083"),
    calendar_writer_url=os.environ.get("CALENDAR_WRITER_URL", "http://calendar-writer:8084"),
    note_writer_url=os.environ.get("NOTE_WRITER_URL", "http://note-writer:8085"),
)


@app.route("/run", methods=["POST"])
def run():
    max_results = request.json.get("max_results", 10) if request.json else 10
    results = pipeline.run(max_results=max_results)
    return jsonify({"results": results, "count": len(results)})


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8086)
