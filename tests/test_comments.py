from datetime import datetime, timedelta, timezone


def _create_client(client, headers, *, name="Acme Company", email="acme@example.com", phone="+79001234567"):
    response = client.post(
        "/clients",
        json={"name": name, "phone": phone, "email": email},
        headers=headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


def _create_task(client, headers, client_id, *, title="Prepare proposal"):
    deadline = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
    response = client.post(
        "/tasks",
        json={
            "client_id": client_id,
            "title": title,
            "description": "Task for comment tests",
            "deadline": deadline,
            "status": "new",
        },
        headers=headers,
    )
    assert response.status_code == 200, response.text
    return response.json()


def _create_comment(client, headers, task_id, text="Need to call the client"):
    response = client.post(
        f"/tasks/{task_id}/comments",
        json={"text": text},
        headers=headers,
    )
    assert response.status_code == 200, response.text
    return response.json()


def test_create_comment(client, manager, auth_headers):
    crm_client = _create_client(client, auth_headers)
    task = _create_task(client, auth_headers, crm_client["id"])

    response = client.post(
        f"/tasks/{task['id']}/comments",
        json={"text": "Need to call the client"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == task["id"]
    assert data["user_id"] == manager["id"]
    assert data["text_comment"] == "Need to call the client"
    assert data["created_at"] is not None


def test_get_task_comments(client, manager, auth_headers):
    crm_client = _create_client(client, auth_headers)
    task = _create_task(client, auth_headers, crm_client["id"])
    first_comment = _create_comment(client, auth_headers, task["id"], "First note")
    second_comment = _create_comment(client, auth_headers, task["id"], "Second note")

    response = client.get(f"/tasks/{task['id']}/comments", headers=auth_headers)

    assert response.status_code == 200
    comments = response.json()
    assert len(comments) == 2
    assert {item["id"] for item in comments} == {first_comment["id"], second_comment["id"]}
    assert all(item["task_id"] == task["id"] for item in comments)


def test_get_comments_for_task_without_comments(client, manager, auth_headers):
    crm_client = _create_client(client, auth_headers)
    task = _create_task(client, auth_headers, crm_client["id"])

    response = client.get(f"/tasks/{task['id']}/comments", headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == []


def test_create_comment_for_nonexistent_task(client, manager, auth_headers):
    response = client.post(
        "/tasks/999999/comments",
        json={"text": "This task does not exist"},
        headers=auth_headers,
    )
    assert response.status_code == 404


def test_get_comments_for_nonexistent_task(client, manager, auth_headers):
    response = client.get("/tasks/999999/comments", headers=auth_headers)
    assert response.status_code == 404


def test_create_comment_for_foreign_task(
    client, manager, auth_headers, other_manager, other_auth_headers
):
    foreign_client = _create_client(client, other_auth_headers, name="Other manager client")
    foreign_task = _create_task(client, other_auth_headers, foreign_client["id"])

    response = client.post(
        f"/tasks/{foreign_task['id']}/comments",
        json={"text": "Must not be added"},
        headers=auth_headers,
    )
    assert response.status_code == 403


def test_get_comments_for_foreign_task(
    client, manager, auth_headers, other_manager, other_auth_headers
):
    foreign_client = _create_client(client, other_auth_headers, name="Other manager client")
    foreign_task = _create_task(client, other_auth_headers, foreign_client["id"])
    _create_comment(client, other_auth_headers, foreign_task["id"], "Private note")

    response = client.get(
        f"/tasks/{foreign_task['id']}/comments",
        headers=auth_headers,
    )
    assert response.status_code == 403


def test_delete_comment(client, manager, auth_headers):
    crm_client = _create_client(client, auth_headers)
    task = _create_task(client, auth_headers, crm_client["id"])
    comment = _create_comment(client, auth_headers, task["id"])

    response = client.delete(f"/comments/{comment['id']}", headers=auth_headers)
    assert response.status_code == 204

    comments_response = client.get(
        f"/tasks/{task['id']}/comments",
        headers=auth_headers,
    )
    assert comments_response.status_code == 200
    assert comments_response.json() == []


def test_delete_foreign_comment(
    client, manager, auth_headers, other_manager, other_auth_headers
):
    foreign_client = _create_client(client, other_auth_headers, name="Other manager client")
    foreign_task = _create_task(client, other_auth_headers, foreign_client["id"])
    comment = _create_comment(client, other_auth_headers, foreign_task["id"], "Owner note")

    response = client.delete(f"/comments/{comment['id']}", headers=auth_headers)
    assert response.status_code == 403

    owner_response = client.get(
        f"/tasks/{foreign_task['id']}/comments",
        headers=other_auth_headers,
    )
    assert owner_response.status_code == 200
    assert len(owner_response.json()) == 1
    assert owner_response.json()[0]["id"] == comment["id"]


def test_delete_nonexistent_comment(client, manager, auth_headers):
    response = client.delete("/comments/999999", headers=auth_headers)
    assert response.status_code == 404
