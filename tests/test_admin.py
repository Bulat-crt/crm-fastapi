from datetime import datetime, timedelta, timezone

import pytest


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
            "description": "Task for admin tests",
            "deadline": deadline,
            "status": "new",
        },
        headers=headers,
    )
    assert response.status_code == 200, response.text
    return response.json()


@pytest.mark.parametrize(
    ("method", "path", "payload"),
    [
        ("get", "/admin/users", None),
        ("get", "/admin/users/1/tasks", None),
        ("get", "/admin/tasks", None),
        ("get", "/admin/clients", None),
        ("get", "/admin/clients/1", None),
        ("get", "/admin/tasks/1", None),
        ("put", "/admin/users/1", {"role": "admin"}),
    ],
)
def test_manager_cannot_access_admin_endpoints(client, manager, auth_headers, method, path, payload):
    response = client.request(
        method,
        path,
        headers=auth_headers,
        json=payload,
    )
    assert response.status_code == 403


def test_unauthenticated_user_cannot_access_admin_endpoints(client):
    response = client.get("/admin/users")
    assert response.status_code == 401


def test_admin_can_list_users(client, admin, admin_auth_headers, manager, other_manager):
    response = client.get("/admin/users", headers=admin_auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 3
    assert data["page"] == 1
    assert data["limit"] == 20
    user_ids = {item["id"] for item in data["items"]}
    assert admin["id"] in user_ids
    assert manager["id"] in user_ids
    assert other_manager["id"] in user_ids


def test_admin_can_list_clients_from_all_managers(
    client, admin, admin_auth_headers, manager, auth_headers, other_manager, other_auth_headers
):
    first_client = _create_client(client, auth_headers, name="First manager client")
    second_client = _create_client(
        client,
        other_auth_headers,
        name="Second manager client",
        email="second@example.com",
        phone="+79000000002",
    )

    response = client.get("/admin/clients", headers=admin_auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert {item["id"] for item in data["items"]} == {first_client["id"], second_client["id"]}
    assert {item["manager_id"] for item in data["items"]} == {manager["id"], other_manager["id"]}


def test_admin_can_list_tasks_from_all_managers(
    client, admin, admin_auth_headers, manager, auth_headers, other_manager, other_auth_headers
):
    first_client = _create_client(client, auth_headers, name="First manager client")
    second_client = _create_client(
        client,
        other_auth_headers,
        name="Second manager client",
        email="second@example.com",
        phone="+79000000002",
    )
    first_task = _create_task(client, auth_headers, first_client["id"], title="First manager task")
    second_task = _create_task(client, other_auth_headers, second_client["id"], title="Second manager task")

    response = client.get("/admin/tasks", headers=admin_auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert {item["id"] for item in data["items"]} == {first_task["id"], second_task["id"]}
    assert {item["manager_id"] for item in data["items"]} == {manager["id"], other_manager["id"]}


def test_admin_can_list_tasks_for_specific_manager(
    client, admin, admin_auth_headers, manager, auth_headers, other_manager, other_auth_headers
):
    first_client = _create_client(client, auth_headers, name="First manager client")
    second_client = _create_client(
        client,
        other_auth_headers,
        name="Second manager client",
        email="second@example.com",
        phone="+79000000002",
    )
    first_task = _create_task(client, auth_headers, first_client["id"], title="First manager task")
    _create_task(client, other_auth_headers, second_client["id"], title="Second manager task")

    response = client.get(
        f"/admin/users/{manager['id']}/tasks",
        headers=admin_auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["id"] == first_task["id"]
    assert data["items"][0]["manager_id"] == manager["id"]


def test_admin_can_get_client_and_task_details(
    client, admin, admin_auth_headers, manager, auth_headers
):
    crm_client = _create_client(client, auth_headers)
    task = _create_task(client, auth_headers, crm_client["id"])

    client_response = client.get(
        f"/admin/clients/{crm_client['id']}",
        headers=admin_auth_headers,
    )
    task_response = client.get(
        f"/admin/tasks/{task['id']}",
        headers=admin_auth_headers,
    )

    assert client_response.status_code == 200
    assert client_response.json()["id"] == crm_client["id"]
    assert task_response.status_code == 200
    assert task_response.json()["id"] == task["id"]


def test_admin_get_nonexistent_task_returns_404(client, admin, admin_auth_headers):
    response = client.get("/admin/tasks/999999", headers=admin_auth_headers)
    assert response.status_code == 404


def test_admin_can_change_user_role(client, admin, admin_auth_headers, other_manager, other_auth_headers):
    response = client.put(
        f"/admin/users/{other_manager['id']}",
        json={"role": "admin"},
        headers=admin_auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["id"] == other_manager["id"]
    assert response.json()["role"] == "admin"

    # Role is loaded from the database for each request, so the existing JWT should now have admin rights.
    access_response = client.get("/admin/users", headers=other_auth_headers)
    assert access_response.status_code == 200
