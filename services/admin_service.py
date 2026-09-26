from sqlalchemy.orm import Session
from fastapi import HTTPException
from schemas import ListResponse, TaskResponse, UserResponse, ClientResponse

from enums.role import Role
from repositories.client_repository import get_all_clients, get_client_by_id
from repositories.user_repository import get_all_users_from_bd, change_role
from repositories.task_repository import get_all_tasks, get_manager_tasks, get_task_by_id

def admin_get_all_users(session: Session, page: int, limit: int):
    offset = (page - 1) * limit
    users, total = get_all_users_from_bd(session, offset, limit)

    return ListResponse[UserResponse](
        items=users,
        total=total,
        page=page,
        limit=limit
    )

def admin_get_all_clients(session: Session, page: int, limit: int):
    offset = (page - 1) * limit
    clients, total = get_all_clients(session, offset, limit)
    return ListResponse[ClientResponse](
        items=clients,
        total=total,
        page=page,
        limit=limit
    )

def admin_get_all_tasks(session: Session, limit: int, page: int):
    offset = (page - 1) * limit
    tasks, total = get_all_tasks(session, offset, limit)
    return ListResponse[TaskResponse](
        items=tasks,
        total=total,
        page=page,
        limit=limit
    )

def admin_get_manager_tasks(session: Session, manager_id: int, page: int, limit: int):
    offset = (page - 1) * limit
    tasks, total = get_manager_tasks(session, manager_id, limit, offset)

    return ListResponse[TaskResponse](
        items=tasks,
        total=total,
        page=page,
        limit=limit
    )

def admin_change_user_role(session: Session, role: Role, user_id: int):
    return change_role(session, role, user_id)

def admin_get_client(session: Session, client_id: int):
    return get_client_by_id(session, client_id)

def admin_get_task(session: Session, task_id: int):
    task = get_task_by_id(session, task_id)

    if task is None:
        raise HTTPException(
            status_code=404,
            detail='Нет такого задания'
        )

