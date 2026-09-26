from fastapi import APIRouter, Depends, Query
from enums.role import Role
from sqlalchemy.orm import Session
from schemas import TaskResponse, UserResponse, ClientResponse, ChangeRole, ListResponse
from data_base import get_db
from dependencies import require_roles
from models import User
from services.admin_service import admin_change_user_role, admin_get_all_clients, admin_get_all_tasks, admin_get_all_users, admin_get_client, admin_get_manager_tasks, admin_get_task

router = APIRouter()

@router.get("/admin/users", response_model=ListResponse[UserResponse])
def get_all_users(
    page: int = Query(1, ge=1), 
    limit: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_db), 
    current_user: User = Depends(require_roles(Role.ADMIN))
):
    return admin_get_all_users(session, page, limit)

@router.get("/admin/users/{manager_id}/tasks", response_model=ListResponse[TaskResponse])
def get_tasks_manager(
    manager_id: int, 
    page: int = Query(1, ge=1), 
    limit: int = Query(20, ge=1, le=100), 
    session: Session = Depends(get_db), 
    current_user: User = Depends(require_roles(Role.ADMIN))):
    return admin_get_manager_tasks(session, manager_id, page, limit)

@router.get("/admin/tasks", response_model=ListResponse[TaskResponse])
def get_all_tasks(
    page: int = Query(1, ge=1), 
    limit: int = Query(20, ge=1, le=100), 
    session: Session = Depends(get_db), 
    current_user: User = Depends(require_roles(Role.ADMIN))
):
    return admin_get_all_tasks(session, limit, page)

@router.get("/admin/clients", response_model=ListResponse[ClientResponse])
def get_all_clients(
    page: int = Query(1, ge=1), 
    limit: int = Query(20, ge=1, le=100), 
    session: Session = Depends(get_db), 
    current_user: User = Depends(require_roles(Role.ADMIN))
):
    return admin_get_all_clients(session, page, limit)

@router.put("/admin/users/{user_id}", response_model=UserResponse)
def change_role_user(
    user_id: int, 
    role: ChangeRole, 
    session: Session = Depends(get_db), 
    current_user: User = Depends(require_roles(Role.ADMIN))
):
    current_role = role.role
    return admin_change_user_role(session, current_role, user_id)

@router.get("/admin/clients/{client_id}", response_model=ClientResponse)
def current_client(
    client_id: int, 
    session: Session = Depends(get_db), 
    current_user: User = Depends(require_roles(Role.ADMIN))
):
    return admin_get_client(session, client_id)

@router.get("/admin/tasks/{task_id}", response_model=TaskResponse)
def current_task(
    task_id: int, 
    session: Session = Depends(get_db), 
    current_user: User = Depends(require_roles(Role.ADMIN))
):
    return admin_get_task(session, task_id)