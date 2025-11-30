from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_create_todo():
    response = client.post("/todos/", json={"title": "Test task", "description": "Integration test"})
    assert response.status_code == 200 or response.status_code == 201
    data = response.json()
    assert data.get("title") == "Test task"
    assert "id" in data


def test_get_all_todos():
    response = client.get("/todos/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_single_todo():
    create_response = client.post("/todos/", json={"title": "Single test", "description": "Check"})
    assert create_response.status_code in (200, 201)
    todo_id = create_response.json()["id"]

    response = client.get(f"/todos/{todo_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == todo_id
    assert data["title"] == "Single test"


def test_update_todo():
    created = client.post("/todos/", json={"title": "Old title", "description": "Test"}).json()
    todo_id = created["id"]

    update_data = {"title": "New title", "description": "Updated description"}
    response = client.put(f"/todos/{todo_id}", json=update_data)

    assert response.status_code == 200
    updated = response.json()
    assert updated["title"] == "New title"
    assert updated["description"] == "Updated description"


def test_delete_todo():
    created = client.post("/todos/", json={"title": "Delete me", "description": ""}).json()
    todo_id = created["id"]

    response = client.delete(f"/todos/{todo_id}")
    assert response.status_code in (200, 204)

    get_response = client.get(f"/todos/{todo_id}")
    assert get_response.status_code in (404, 400, 422)


def test_get_nonexistent_todo():
    response = client.get("/todos/999999")
    assert response.status_code in (404, 400, 422)
