from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from schemas import TaskCreate, TaskResponse, TaskUpdate, ListResponse
from enums.status import Status
from enums.task import TaskSort
from enums.sort_order import SortOrder
from data_base import get_db
from dependencies import get_current_user
from models import User
from services.task_service import create_client_task, get_all_manager_tasks, get_current_task_manager, update_task_manager, delete_task_manager


router = APIRouter()

@router.post("/tasks", response_model=TaskResponse)
def create_task(client_task: TaskCreate, current_user: User = Depends(get_current_user), session: Session = Depends(get_db)):
    acces_create_task = create_client_task(
        session,
        client_task.title,
        client_task.description,
        client_task.status,
        client_task.deadline,
        current_user.id,
        client_task.client_id
    )

    if acces_create_task is None:
        raise HTTPException(
            status_code=404,
            detail='Нет такого клиента'
        )

    elif acces_create_task is False:
        raise HTTPException(
            status_code=403,
            detail='Не ваш клиент'
        )

    return acces_create_task

@router.get("/tasks", response_model=ListResponse[TaskResponse])
def get_tasks_current_manager(
    order: SortOrder = Query(SortOrder.DESC),
    sort: TaskSort = Query(TaskSort.CREATED_AT),
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Status | None = None,
    search: str | None = None
):
    manager_id = current_user.id
    tasks = get_all_manager_tasks(session, manager_id, page, limit, sort, order, status, search)

    return tasks

@router.get("/tasks/{task_id}", response_model=TaskResponse)
def get_current_task(task_id: int, current_manager: User = Depends(get_current_user), session: Session = Depends(get_db)):
    manager_id = current_manager.id
    task = get_current_task_manager(session, manager_id, task_id)

    if task is False:
        raise HTTPException(
            status_code=403,
            detail='Не ваш клиент'
        )

    elif task is None:
        raise HTTPException(
            status_code=404,
            detail='Нет такой задачи'
        )

    return task

@router.put("/tasks/{task_id}", response_model=TaskResponse)
def update_current_task(task_update: TaskUpdate, task_id : int, current_manager: User = Depends(get_current_user), session: Session = Depends(get_db)):
    manager_id = current_manager.id
    new_title = task_update.title
    new_description = task_update.description
    new_status = task_update.status
    new_deadline = task_update.deadline
    acces_update = update_task_manager(session, manager_id, task_id, new_title, new_description, new_status, new_deadline)

    if acces_update is False:
        raise HTTPException(
            status_code=403,
            detail='Не ваш клиент'
        )
    
    elif acces_update is None:
        raise HTTPException(
            status_code=404,
            detail='Нет такой задачи'
        )

    return acces_update

@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_current_task(
    task_id: int, 
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_db)
):
    manager_id = current_user.id
    acces_delete = delete_task_manager(session, manager_id, task_id)

    if acces_delete is False:
        raise HTTPException(
            status_code=403,
            detail='Не ваша задача'
        )
    
    elif acces_delete is None:
        raise HTTPException(
            status_code=404,
            detail='Нет такой задачи'
        )

    return None