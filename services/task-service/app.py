import os
from datetime import datetime, timezone
from flask import Flask, request, jsonify
from flask_cors import CORS
from db import Task, Label, init_db


def _get_or_create_labels(session, label_names):
    labels = []
    for name in label_names:
        label = session.query(Label).filter_by(name=name).first()
        if not label:
            label = Label(name=name)
            session.add(label)
        labels.append(label)
    return labels


def create_app(database_url=None):
    app = Flask(__name__)
    CORS(app)
    url = database_url or os.environ.get("DATABASE_URL", "sqlite:///tasks.db")
    Session = init_db(url)

    @app.route("/health")
    def health():
        return jsonify({"status": "ok"})

    @app.route("/tasks", methods=["POST"])
    def create_task():
        data = request.json
        if not data or "title" not in data:
            return jsonify({"error": "title required"}), 400
        session = Session()
        task = Task(title=data["title"], description=data.get("description"))
        if "labels" in data:
            task.labels = _get_or_create_labels(session, data["labels"])
        session.add(task)
        session.commit()
        result = task.to_dict()
        session.close()
        return jsonify(result), 201

    @app.route("/tasks", methods=["GET"])
    def list_tasks():
        session = Session()
        label_filter = request.args.get("label")
        if label_filter:
            tasks = session.query(Task).filter(Task.labels.any(Label.name == label_filter)).all()
        else:
            tasks = session.query(Task).all()
        result = [t.to_dict() for t in tasks]
        session.close()
        return jsonify(result)

    @app.route("/tasks/<int:task_id>", methods=["GET"])
    def get_task(task_id):
        session = Session()
        task = session.get(Task, task_id)
        if not task:
            session.close()
            return jsonify({"error": "not found"}), 404
        result = task.to_dict()
        session.close()
        return jsonify(result)

    @app.route("/tasks/<int:task_id>", methods=["PUT"])
    def update_task(task_id):
        data = request.json
        session = Session()
        task = session.get(Task, task_id)
        if not task:
            session.close()
            return jsonify({"error": "not found"}), 404
        if "title" in data:
            task.title = data["title"]
        if "description" in data:
            task.description = data["description"]
        if "completed_at" in data:
            if data["completed_at"]:
                task.completed_at = datetime.fromisoformat(data["completed_at"]).replace(tzinfo=timezone.utc)
            else:
                task.completed_at = None
        if "labels" in data:
            task.labels = _get_or_create_labels(session, data["labels"])
        task.updated_at = datetime.now(timezone.utc)
        session.commit()
        result = task.to_dict()
        session.close()
        return jsonify(result)

    @app.route("/tasks/<int:task_id>", methods=["DELETE"])
    def delete_task(task_id):
        session = Session()
        task = session.get(Task, task_id)
        if not task:
            session.close()
            return jsonify({"error": "not found"}), 404
        session.delete(task)
        session.commit()
        session.close()
        return "", 204

    @app.route("/labels", methods=["POST"])
    def create_label():
        data = request.json
        if not data or "name" not in data:
            return jsonify({"error": "name required"}), 400
        session = Session()
        if session.query(Label).filter_by(name=data["name"]).first():
            session.close()
            return jsonify({"error": "label already exists"}), 409
        label = Label(name=data["name"])
        session.add(label)
        session.commit()
        result = label.to_dict()
        session.close()
        return jsonify(result), 201

    @app.route("/labels", methods=["GET"])
    def list_labels():
        session = Session()
        labels = session.query(Label).all()
        result = [l.to_dict() for l in labels]
        session.close()
        return jsonify(result)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=8090)
