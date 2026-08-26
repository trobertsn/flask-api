import app

client = app.app.test_client()


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "healthy"}


def test_create_and_get_task():
    response = client.post("/tasks", json={"title": "test task"})
    assert response.status_code == 201
    task_id = response.get_json()["id"]
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.get_json()["title"] == "test task"


def test_missing_title_returns_400():
    response = client.post("/tasks", json={})
    assert response.status_code == 400
