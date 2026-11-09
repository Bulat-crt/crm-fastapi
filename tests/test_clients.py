#python -m pytest -v
def test_create_client(client, manager, auth_headers):
    response = client.post(
        '/clients',
        json={
            "name": "Acme Company",
            "phone": "+79001234567",
            "email": "acme@example.com"
        },
        headers=auth_headers
    )

    assert response.status_code == 201

    data = response.json()

    assert data['name'] == 'Acme Company'
    assert data['phone'] == '+79001234567'
    assert data['email'] == 'acme@example.com'
    assert data['manager_id'] == manager['id']


def test_get_all_clients(client, manager, auth_headers):
    first_response = client.post(
        '/clients',
        json={
            "name": "Acme Company",
            "phone": "+79001234567",
            "email": "acme@example.com"
        },
        headers=auth_headers
    )

    assert first_response.status_code == 201

    second_response = client.post(
        '/clients',
        json={
            "name": "Acne Company",
            "phone": "+79001234567",
            "email": "acme@example.com"
        },
        headers=auth_headers
    )

    assert second_response.status_code == 201

    third_response = client.get(
        '/clients',
        headers=auth_headers
    )

    assert third_response.status_code == 200

    first_data = first_response.json()
    second_data = second_response.json()
    third_data = third_response.json()

    assert third_data['limit'] == 20
    assert third_data['page'] == 1
    assert third_data['total'] == 2
    assert any(data['name'] == second_data['name'] for data in third_data['items'])
    assert any(data['name'] == first_data['name'] for data in third_data['items'])


def test_get_client_by_id(client, manager, auth_headers):
    first_response = client.post(
        '/clients',
        json={
            "name": "Acme Company",
            "phone": "+79001234567",
            "email": "acme@example.com"
        },
        headers=auth_headers
    )

    assert first_response.status_code == 201

    data = first_response.json()
    client_id = data['id']

    second_response = client.get(
        f'/clients/{client_id}',
        headers=auth_headers
    )

    assert second_response.status_code == 200
    current_client = second_response.json()

    assert current_client['id'] == data['id']


def test_get_nonexistent_client(client, manager, auth_headers):
    client_id = 999999
    response = client.get(
        f'/clients/{client_id}',
        headers=auth_headers
    )

    assert response.status_code == 404


def test_update_client(client, manager, auth_headers):
    first_response = client.post(
        '/clients',
        json={
            "name": "Acme Company",
            "phone": "+79001234567",
            "email": "acme@example.com"
        },
        headers=auth_headers
    )

    assert first_response.status_code == 201

    client_id = first_response.json()['id']

    second_response = client.put(
        f'/clients/{client_id}',
        json={
            "name": "Updated Company",
            "phone": "+79009876543",
            "email": "updated@example.com"
        },
        headers=auth_headers
    )

    assert second_response.status_code == 200

    data = second_response.json()

    assert data['id'] == client_id
    assert data['name'] == "Updated Company"
    assert data['phone'] == "+79009876543"
    assert data['email'] == "updated@example.com"
    assert data['manager_id'] == manager['id']


def test_update_foreign_client(
    client,
    manager,
    auth_headers,
    other_manager,
    other_auth_headers
):
    first_response = client.post(
        '/clients',
        json={
            "name": "Acme Company",
            "phone": "+79001234567",
            "email": "acme@example.com"
        },
        headers=auth_headers
    )

    assert first_response.status_code == 201

    client_id = first_response.json()['id']

    second_response = client.put(
        f'/clients/{client_id}',
        json={
            "name": "Updated Company",
            "phone": "+79009876543",
            "email": "updated@example.com"
        },
        headers=other_auth_headers
    )

    assert second_response.status_code == 403

    third_response = client.get(
        f'/clients/{client_id}',
        headers=auth_headers
    )

    assert third_response.status_code == 200

    data = third_response.json()

    assert data['name'] == "Acme Company"
    assert data['phone'] == "+79001234567"
    assert data['email'] == "acme@example.com"
    assert data['manager_id'] == manager['id']

def test_delete_client(client, manager, auth_headers):
    first_response = client.post(
        '/clients',
        json={
            "name": "Acme Company",
            "phone": "+79001234567",
            "email": "acme@example.com"
        },
        headers=auth_headers
    )

    assert first_response.status_code == 201

    client_id = first_response.json()['id'] 

    second_response = client.delete(
        f'/clients/{client_id}',
        headers=auth_headers
    )

    assert second_response.status_code == 204

    third_response = client.get(
        f'/clients/{client_id}',
        headers=auth_headers
    )

    assert third_response.status_code == 404

def test_delete_foreign_client(client, manager, auth_headers, other_auth_headers, other_manager):
    first_response = client.post(
        '/clients',
        json={
            "name": "Acme Company",
            "phone": "+79001234567",
            "email": "acme@example.com"
        },
        headers=auth_headers
    )

    assert first_response.status_code == 201

    client_id = first_response.json()['id'] 

    second_response = client.delete(
        f'/clients/{client_id}',
        headers=other_auth_headers
    )

    assert second_response.status_code == 403

    third_response = client.get(
        f'/clients/{client_id}',
        headers=auth_headers
    )

    assert third_response.status_code == 200

    data = third_response.json()

    assert data['manager_id'] == manager['id']

def test_get_foreign_client(
    client,
    manager,
    auth_headers,
    other_manager,
    other_auth_headers
):
    first_response = client.post(
        '/clients',
        json={
            "name": "Acme Company",
            "phone": "+79001234567",
            "email": "acme@example.com"
        },
        headers=auth_headers
    )

    assert first_response.status_code == 201

    client_id = first_response.json()['id'] 

    second_response = client.get(
        f'/clients/{client_id}',
        headers=other_auth_headers
    )

    assert second_response.status_code == 403