# CRM Backend

A backend for a simple Customer Relationship Management (CRM) system built with FastAPI, PostgreSQL and SQLAlchemy.

The project provides authentication, role-based authorization, client management, task management and comments.

## Features

* User registration and authentication
* JWT access tokens
* Role-based authorization (`manager` / `admin`)
* Client CRUD
* Task CRUD
* Task comments
* Pagination
* Search
* Filtering by task status
* Sorting
* PostgreSQL database
* SQLAlchemy ORM
* Alembic migrations
* Pydantic validation
* Swagger/OpenAPI documentation

## Project Structure

```text
CRM/
├── alembic/
├── enums/
├── repositories/
├── routes/
├── services/
├── .env
├── .env.example
├── .gitignore
├── alembic.ini
├── config.py
├── data_base.py
├── dependencies.py
├── main.py
├── models.py
└── schemas.py
```

## Requirements

* Python 3.13+
* PostgreSQL
* pip

## Installation

Clone the repository:

```bash
git clone <https://github.com/Bulat-crt?tab=repositories>
cd CRM
```

Create and activate a virtual environment:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in the project root.

Example:

```env
DATABASE_URL=postgresql+psycopg2://username:password@localhost:5432/crm
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

A template is provided in `.env.example`.

## Database

Make sure PostgreSQL is running and the `crm` database exists.

Apply Alembic migrations:

```bash
alembic upgrade head
```

## Run the Application

Start the FastAPI server:

```bash
uvicorn main:app --reload
```

The application will be available at:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

## Authentication

The API uses JWT Bearer authentication.

After logging in, the access token can be provided through Swagger's `Authorize` button.

Protected endpoints require:

```text
Authorization: Bearer <access_token>
```

## Roles

### Manager

Managers can work with their own clients and tasks.

### Admin

Administrators have access to all users, clients and tasks and can change user roles.

## API Overview

### Authentication

```text
POST /auth/register
POST /auth/login
GET  /users/me
```

### Clients

```text
POST   /clients
GET    /clients
GET    /clients/{client_id}
PUT    /clients/{client_id}
DELETE /clients/{client_id}
```

### Tasks

```text
POST   /tasks
GET    /tasks
GET    /tasks/{task_id}
PUT    /tasks/{task_id}
DELETE /tasks/{task_id}
```

### Comments

```text
POST   /tasks/{task_id}/comments
GET    /tasks/{task_id}/comments
DELETE /comments/{comment_id}
```

### Admin

```text
GET /admin/users
GET /admin/users/{manager_id}/tasks
GET /admin/tasks
GET /admin/clients

GET /admin/clients/{client_id}
GET /admin/tasks/{task_id}

PUT /admin/users/{user_id}
```

## Architecture

The project follows a layered architecture:

```text
Routes
  ↓
Services
  ↓
Repositories
  ↓
SQLAlchemy
  ↓
PostgreSQL
```

* **Routes** handle HTTP requests and responses.
* **Services** contain business logic and access checks.
* **Repositories** contain database queries.
* **Models** define database tables and relationships.
* **Schemas** define request and response validation.
* **Dependencies** handle authentication and role-based authorization.

## License

This project was created as a learning project.
