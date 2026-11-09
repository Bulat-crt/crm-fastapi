import os
import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from data_base import get_db
from main import app


load_dotenv()

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

if not TEST_DATABASE_URL:
    raise RuntimeError("TEST_DATABASE_URL is not set")

test_engine = create_engine(TEST_DATABASE_URL)

TestSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False
)

def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def clean_database():
    with test_engine.begin() as connection:
        connection.execute(
            text("TRUNCATE TABLE users, clients, tasks, comments RESTART IDENTITY CASCADE")
        )

@pytest.fixture
def client(clean_database):
    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def manager(client):
    response = client.post(
        "/auth/register",
        json={
            "name": "Test Manager",
            "email": "manager@test.com",
            "password": "123321123"
        }
    )

    assert response.status_code == 201

    return response.json()


@pytest.fixture
def auth_headers(client, manager):
    response = client.post(
        "/auth/login",
        data={
            "username": manager["email"],
            "password": "123321123"
        }
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }

@pytest.fixture
def other_manager(client):
    response = client.post(
        "/auth/register",
        json={
            'name': "Other Manager",
            'email': "other@test.com",
            'password': "123321123"
        }
    )

    assert response.status_code == 201

    return response.json()

@pytest.fixture
def other_auth_headers(client, other_manager):
    response = client.post(
        "/auth/login",
        data={
            "username": other_manager["email"],
            "password": "123321123"
        }
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }