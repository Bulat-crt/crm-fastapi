from datetime import datetime, timedelta, timezone


def _create_client(client, headers, *, name="Acme Company", email="acme@example.com", phone="+79001234567"):
    response = client.post(
        "/clients",
        json={"name": name, "phone": phone, "email": email},
        headers=headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


def _create_task(
    client,
    headers,
    client_id,
    *,
    title="Prepare proposal",
    description="Prepare a commercial proposal",
    status="new",
):
    deadline = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
    response = client.post(
        "/tasks",
        json={
            "client_id": client_id,
            "title": title,
            "description": description,
            "deadline": deadline,
            "status": status,
        },
        headers=headers,
    )
    assert response.status_code == 200, response.text
    return response.json()


def test_create_task_for_own_client(client, manager, auth_headers):
    crm_client = _create_client(client, auth_headers)
    task = _create_task(client, auth_headers, crm_client["id"])

    assert task["title"] == "Prepare proposal"
    assert task["description"] == "Prepare a commercial proposal"
    assert task["status"] == "new"
    assert task["client_id"] == crm_client["id"]
    assert task["manager_id"] == manager["id"]
    assert task["deadline"] is not None
    assert task["created_at"] is not None


def test_create_task_for_nonexistent_client(client, manager, auth_headers):
    deadline = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
    response = client.post(
        "/tasks",
        json={
            "client_id": 999999,
            "title": "Orphan task",
            "description": "Client does not exist",
            "deadline": deadline,
            "status": "new",
        },
        headers=auth_headers,
    )

    assert response.status_code == 404


def test_create_task_for_foreign_client(
    client, manager, auth_headers, other_manager, other_auth_headers
):
    foreign_client = _create_client(client, other_auth_headers, name="Other manager client")
    deadline = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()

    response = client.post(
        "/tasks",
        json={
            "client_id": foreign_client["id"],
            "title": "Foreign task",
            "description": "Must not be created",
            "deadline": deadline,
            "status": "new",
        },
        headers=auth_headers,
    )

    assert response.status_code == 403


def test_get_task_by_id(client, manager, auth_headers):
    crm_client = _create_client(client, auth_headers)
    created_task = _create_task(client, auth_headers, crm_client["id"])

    response = client.get(f"/tasks/{created_task['id']}", headers=auth_headers)

    assert response.status_code == 200
    task = response.json()
    assert task["id"] == created_task["id"]
    assert task["client_id"] == crm_client["id"]
    assert task["manager_id"] == manager["id"]
    assert task["title"] == created_task["title"]


def test_get_nonexistent_task(client, manager, auth_headers):
    response = client.get("/tasks/999999", headers=auth_headers)
    assert response.status_code == 404


def test_get_foreign_task(client, manager, auth_headers, other_manager, other_auth_headers):
    foreign_client = _create_client(client, other_auth_headers, name="Other manager client")
    foreign_task = _create_task(client, other_auth_headers, foreign_client["id"])

    response = client.get(f"/tasks/{foreign_task['id']}", headers=auth_headers)

    assert response.status_code == 403


def test_get_tasks_only_for_current_manager(
    client, manager, auth_headers, other_manager, other_auth_headers
):
    own_client = _create_client(client, auth_headers, name="Own client")
    foreign_client = _create_client(client, other_auth_headers, name="Foreign client")
    own_task = _create_task(client, auth_headers, own_client["id"], title="Own task")
    _create_task(client, other_auth_headers, foreign_client["id"], title="Foreign task")

    response = client.get("/tasks", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["id"] == own_task["id"]
    assert data["items"][0]["manager_id"] == manager["id"]


def test_filter_tasks_by_status_and_search(client, manager, auth_headers):
    crm_client = _create_client(client, auth_headers)
    matching_task = _create_task(
        client,
        auth_headers,
        crm_client["id"],
        title="Prepare Acme proposal",
        description="Discuss Acme contract",
        status="in_progress",
    )
    _create_task(
        client,
        auth_headers,
        crm_client["id"],
        title="Call supplier",
        description="Check delivery date",
        status="new",
    )

    response = client.get(
        "/tasks",
        params={"status": "in_progress", "search": "Acme"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["id"] == matching_task["id"]
    assert data["items"][0]["status"] == "in_progress"


def test_tasks_pagination_and_sorting(client, manager, auth_headers):
    crm_client = _create_client(client, auth_headers)
    _create_task(client, auth_headers, crm_client["id"], title="Gamma task")
    _create_task(client, auth_headers, crm_client["id"], title="Alpha task")
    _create_task(client, auth_headers, crm_client["id"], title="Beta task")

    first_page = client.get(
        "/tasks",
        params={"page": 1, "limit": 2, "sort": "title", "order": "asc"},
        headers=auth_headers,
    )
    second_page = client.get(
        "/tasks",
        params={"page": 2, "limit": 2, "sort": "title", "order": "asc"},
        headers=auth_headers,
    )

    assert first_page.status_code == 200
    assert second_page.status_code == 200
    first_data = first_page.json()
    second_data = second_page.json()
    assert first_data["total"] == 3
    assert first_data["page"] == 1
    assert first_data["limit"] == 2
    assert [item["title"] for item in first_data["items"]] == ["Alpha task", "Beta task"]
    assert [item["title"] for item in second_data["items"]] == ["Gamma task"]


def test_update_task(client, manager, auth_headers):
    crm_client = _create_client(client, auth_headers)
    task = _create_task(client, auth_headers, crm_client["id"])
    new_deadline = (datetime.now(timezone.utc) + timedelta(days=14)).isoformat()

    response = client.put(
        f"/tasks/{task['id']}",
        json={
            "title": "Updated proposal",
            "description": "Updated description",
            "status": "done",
            "deadline": new_deadline,
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task["id"]
    assert data["title"] == "Updated proposal"
    assert data["description"] == "Updated description"
    assert data["status"] == "done"
    assert data["manager_id"] == manager["id"]
    assert data["client_id"] == crm_client["id"]

    persisted = client.get(f"/tasks/{task['id']}", headers=auth_headers)
    assert persisted.status_code == 200
    assert persisted.json()["title"] == "Updated proposal"


def test_update_foreign_task(client, manager, auth_headers, other_manager, other_auth_headers):
    foreign_client = _create_client(client, other_auth_headers, name="Other manager client")
    foreign_task = _create_task(client, other_auth_headers, foreign_client["id"])
    new_deadline = (datetime.now(timezone.utc) + timedelta(days=14)).isoformat()

    response = client.put(
        f"/tasks/{foreign_task['id']}",
        json={
            "title": "Hacked task",
            "description": "Must not change",
            "status": "done",
            "deadline": new_deadline,
        },
        headers=auth_headers,
    )

    assert response.status_code == 403
    owner_response = client.get(f"/tasks/{foreign_task['id']}", headers=other_auth_headers)
    assert owner_response.status_code == 200
    assert owner_response.json()["title"] == foreign_task["title"]


def test_update_nonexistent_task(client, manager, auth_headers):
    deadline = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
    response = client.put(
        "/tasks/999999",
        json={
            "title": "Updated task",
            "description": "Does not exist",
            "status": "done",
            "deadline": deadline,
        },
        headers=auth_headers,
    )
    assert response.status_code == 404


def test_delete_task(client, manager, auth_headers):
    crm_client = _create_client(client, auth_headers)
    task = _create_task(client, auth_headers, crm_client["id"])

    response = client.delete(f"/tasks/{task['id']}", headers=auth_headers)
    assert response.status_code == 204

    get_response = client.get(f"/tasks/{task['id']}", headers=auth_headers)
    assert get_response.status_code == 404


def test_delete_foreign_task(client, manager, auth_headers, other_manager, other_auth_headers):
    foreign_client = _create_client(client, other_auth_headers, name="Other manager client")
    foreign_task = _create_task(client, other_auth_headers, foreign_client["id"])

    response = client.delete(f"/tasks/{foreign_task['id']}", headers=auth_headers)
    assert response.status_code == 403

    owner_response = client.get(f"/tasks/{foreign_task['id']}", headers=other_auth_headers)
    assert owner_response.status_code == 200


def test_delete_nonexistent_task(client, manager, auth_headers):
    response = client.delete("/tasks/999999", headers=auth_headers)
    assert response.status_code == 404
