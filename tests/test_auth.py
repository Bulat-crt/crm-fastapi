from datetime import datetime, timedelta, timezone
from jose import jwt
from config import settings

def test_succes_registration(client):
    response = client.post(
        "/auth/register",
        json={
            'name':'Example',
            'email': 'user@example.com',
            'password': '123321123'
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data['name'] == 'Example'
    assert data['email'] == 'user@example.com'
    assert 'password' not in data
    assert 'password_hash' not in data

def test_failed_registration_exited_email(client):
    first_response = client.post(
        "/auth/register",
        json={
            'name':'Example',
            'email': 'user@example.com',
            'password': '123321123'
        }
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/auth/register",
        json={
            'name':'Example',
            'email': 'user@example.com',
            'password': '123321123'
        }
    )

    assert second_response.status_code == 409


def test_bad_email(client):
    response = client.post(
        "/auth/register",
        json={
            'name':'Example',
            'email': 'sda',
            'password': '123321123'
        }
    )

    assert response.status_code == 422

def test_success_login(client):
    first_response = client.post(
        "/auth/register",
        json={
            'name':'Example',
            'email':'user@example.com',
            'password': '123321123'
        }
    )

    assert first_response.status_code == 201

    second_response = client.post(
        '/auth/login',
        data={
            'username':'user@example.com',
            'password': '123321123'
        }
    )

    assert second_response.status_code == 200


def test_false_password(client):
    first_response = client.post(
        "/auth/register",
        json={
            'name':'Example',
            'email':'user@example.com',
            'password': '123321123'
        }
    )

    assert first_response.status_code == 201

    second_response = client.post(
        '/auth/login',
        data={
            'username':'user@example.com',
            'password': '132123321'
        }
    )

    assert second_response.status_code == 401

def test_client_none(client):
    response = client.post(
        '/auth/login',
        data={
            'username':'user@example.com',
            'password': '132123321'
        }
    )

    assert response.status_code == 401

def test_get_user_without_token(client):
    response = client.get(
        '/users/me'
    )

    assert response.status_code == 401

def test_get_user_with_token(client):
    first_response = client.post(
        "/auth/register",
        json={
            'name':'Example',
            'email':'user@example.com',
            'password': '123321123'
        }
    )

    assert first_response.status_code == 201

    second_response = client.post(
        '/auth/login',
        data={
            'username':'user@example.com',
            'password': '123321123'
        }
    )

    assert second_response.status_code == 200

    token = second_response.json()['access_token']

    headers = {
        'Authorization': f'Bearer {token}'
    }

    third_response = client.get(
        '/users/me',
        headers=headers
    )

    assert third_response.status_code == 200

    data = third_response.json()

    assert data['name'] == 'Example'
    assert data['email'] == 'user@example.com'
    assert data['role'] is not None
    assert data['created_at'] is not None


def test_expired_token(client):
    registr = client.post(
        '/auth/register',
        json={
            'name': 'Example',
            'email': 'user@example.com',
            'password': '123321123'
        }
    )
    
    assert registr.status_code == 201

    user_id = registr.json()['id']


    expired_token = jwt.encode(
        {
            'sub': str(user_id),
            'exp': datetime.now(timezone.utc) - timedelta(minutes=1)
        },
        settings.secret_key,
        algorithm=settings.algorithm
    )

    response = client.get(
        '/users/me',
        headers={
            'Authorization': f'Bearer {expired_token}'
        }
    )

    assert response.status_code == 401