from sqlalchemy.orm import Session
from datetime import datetime
from enums.status import Status
from enums.task import TaskSort
from enums.sort_order import SortOrder
from schemas import ListResponse, TaskResponse
from repositories.client_repository import get_client_by_id
from repositories.task_repository import create_task, get_manager_tasks, get_task_by_id, update_task, delete_task
def create_client_task(session: Session, 
    title: str, 
    description: str, 
    status: Status, 
    deadline: datetime, 
    manager_id: int, 
    client_id: int
):
    client = get_client_by_id(session, client_id)
    if client is None:
        return None

    if client.manager_id != manager_id:
        return False
    
    task = create_task(session, title, description, status, deadline, manager_id, client_id)
    return task

def get_all_manager_tasks(
    session: Session, 
    manager_id: int,
    page: int,
    limit: int,
    sort: TaskSort,
    order: SortOrder,
    status: Status | None,
    search: str | None
) -> ListResponse[TaskResponse]:
    offset = (page - 1) * limit
    tasks, total = get_manager_tasks(session, manager_id, limit, offset, sort, order, status, search)

    return ListResponse[TaskResponse](
        items=tasks,
        total=total,
        page=page,
        limit=limit
    )

def get_current_task_manager(
    session: Session, 
    manager_id: int, 
    task_id: int
):
    task = get_task_by_id(session, task_id)

    if task is None:
        return None

    elif task.manager_id != manager_id:
        return False

    return task

def update_task_manager(
    session: Session, 
    manager_id: int, 
    task_id: int,
    new_title: str,
    new_description: str,
    new_status: Status,
    new_deadline: datetime
):
    task = get_task_by_id(session, task_id)

    if task is None:
        return None
    
    elif task.manager_id != manager_id:
        return False
    
    update_task(session, task_id, new_title, new_description, new_status, new_deadline)

    return task

def delete_task_manager(
    session: Session,
    manager_id: int,
    task_id: int
):
    task = get_task_by_id(session, task_id)

    if task is None:
        return None
    
    elif task.manager_id != manager_id:
        return False
    
    delete_task(session, task_id)

    return True   