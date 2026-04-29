import pytest
from app import create_app


@pytest.fixture
def client():
    app = create_app("sqlite:///:memory:")
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}


def test_create_task(client):
    resp = client.post("/tasks", json={"title": "Buy milk"})
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["title"] == "Buy milk"
    assert data["description"] is None
    assert data["completed_at"] is None
    assert data["labels"] == []
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_create_task_with_description(client):
    resp = client.post("/tasks", json={"title": "Buy milk", "description": "Whole milk"})
    assert resp.status_code == 201
    assert resp.get_json()["description"] == "Whole milk"


def test_create_task_missing_title(client):
    resp = client.post("/tasks", json={})
    assert resp.status_code == 400


def test_create_task_no_body(client):
    resp = client.post("/tasks", content_type="application/json")
    assert resp.status_code == 400


def test_create_task_with_labels(client):
    resp = client.post("/tasks", json={"title": "Buy milk", "labels": ["grocery", "urgent"]})
    assert resp.status_code == 201
    data = resp.get_json()
    assert sorted(data["labels"]) == ["grocery", "urgent"]


def test_list_tasks_empty(client):
    resp = client.get("/tasks")
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_list_tasks(client):
    client.post("/tasks", json={"title": "Task 1"})
    client.post("/tasks", json={"title": "Task 2"})
    resp = client.get("/tasks")
    assert resp.status_code == 200
    assert len(resp.get_json()) == 2


def test_get_task(client):
    create_resp = client.post("/tasks", json={"title": "Buy milk"})
    task_id = create_resp.get_json()["id"]
    resp = client.get(f"/tasks/{task_id}")
    assert resp.status_code == 200
    assert resp.get_json()["title"] == "Buy milk"


def test_get_task_not_found(client):
    resp = client.get("/tasks/999")
    assert resp.status_code == 404


def test_update_task(client):
    create_resp = client.post("/tasks", json={"title": "Buy milk"})
    task_id = create_resp.get_json()["id"]
    resp = client.put(f"/tasks/{task_id}", json={"title": "Buy oat milk", "description": "From store"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["title"] == "Buy oat milk"
    assert data["description"] == "From store"


def test_update_task_complete(client):
    create_resp = client.post("/tasks", json={"title": "Buy milk"})
    task_id = create_resp.get_json()["id"]
    resp = client.put(f"/tasks/{task_id}", json={"completed_at": "2026-04-29T12:00:00"})
    assert resp.status_code == 200
    assert resp.get_json()["completed_at"] is not None


def test_update_task_labels(client):
    create_resp = client.post("/tasks", json={"title": "Buy milk", "labels": ["grocery"]})
    task_id = create_resp.get_json()["id"]
    resp = client.put(f"/tasks/{task_id}", json={"labels": ["grocery", "urgent"]})
    assert resp.status_code == 200
    assert sorted(resp.get_json()["labels"]) == ["grocery", "urgent"]


def test_update_task_remove_labels(client):
    create_resp = client.post("/tasks", json={"title": "Buy milk", "labels": ["grocery"]})
    task_id = create_resp.get_json()["id"]
    resp = client.put(f"/tasks/{task_id}", json={"labels": []})
    assert resp.status_code == 200
    assert resp.get_json()["labels"] == []


def test_update_task_not_found(client):
    resp = client.put("/tasks/999", json={"title": "Nope"})
    assert resp.status_code == 404


def test_delete_task(client):
    create_resp = client.post("/tasks", json={"title": "Buy milk"})
    task_id = create_resp.get_json()["id"]
    resp = client.delete(f"/tasks/{task_id}")
    assert resp.status_code == 204
    resp = client.get(f"/tasks/{task_id}")
    assert resp.status_code == 404


def test_delete_task_not_found(client):
    resp = client.delete("/tasks/999")
    assert resp.status_code == 404


def test_filter_tasks_by_label(client):
    client.post("/tasks", json={"title": "Buy milk", "labels": ["grocery"]})
    client.post("/tasks", json={"title": "Fix bug", "labels": ["work"]})
    client.post("/tasks", json={"title": "Buy eggs", "labels": ["grocery"]})
    resp = client.get("/tasks?label=grocery")
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 2
    assert all("grocery" in t["labels"] for t in data)


def test_filter_tasks_by_label_empty(client):
    client.post("/tasks", json={"title": "Buy milk", "labels": ["grocery"]})
    resp = client.get("/tasks?label=work")
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_create_label(client):
    resp = client.post("/labels", json={"name": "grocery"})
    assert resp.status_code == 201
    assert resp.get_json()["name"] == "grocery"


def test_create_label_duplicate(client):
    client.post("/labels", json={"name": "grocery"})
    resp = client.post("/labels", json={"name": "grocery"})
    assert resp.status_code == 409


def test_list_labels(client):
    client.post("/labels", json={"name": "grocery"})
    client.post("/labels", json={"name": "work"})
    resp = client.get("/labels")
    assert resp.status_code == 200
    assert len(resp.get_json()) == 2


def test_labels_created_implicitly(client):
    client.post("/tasks", json={"title": "Buy milk", "labels": ["grocery"]})
    resp = client.get("/labels")
    assert resp.status_code == 200
    names = [l["name"] for l in resp.get_json()]
    assert "grocery" in names
