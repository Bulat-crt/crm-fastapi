from datetime import datetime
from enums.status import Status
from sqlalchemy import select, func, or_
from sqlalchemy.orm import Session
from enums.task import TaskSort
from enums.sort_order import SortOrder
from models import Task, User, Client

TASK_SORT_FIELDS = {
    TaskSort.DEADLINE: Task.deadline,
    TaskSort.CREATED_AT: Task.created_at,
    TaskSort.TITLE: Task.title,
}




def create_task(
    session: Session,
    title: str,
    description: str,
    status: str,
    deadline: datetime,
    manager: User,
    client: Client
) -> Task:

    task = Task(
        title=title,
        description=description,
        status=status,
        deadline=deadline,
        manager_id=manager,
        client_id=client
    )

    session.add(task)
    session.commit()
    session.refresh(task)

    return task

def get_task_by_id(
    session: Session,
    task_id: int
) -> Task | None:
    statement = select(Task).where(Task.id == task_id)
    task = session.scalars(statement).first()

    return task

def get_manager_tasks(
    session: Session,
    manager_id: int,
    limit: int,
    offset: int,
    sort: TaskSort = TaskSort.CREATED_AT,
    order: SortOrder = SortOrder.DESC,
    status: Status | None = None,
    search: str | None = None
) -> tuple[list[Task], int]:
    sort_column = TASK_SORT_FIELDS[sort]
    if order == SortOrder.ASC:
        order_by = sort_column.asc()
    else:
        order_by = sort_column.desc()

    conditions = [Task.manager_id == manager_id]

    if status is not None:
        conditions.append(Task.status == status)
    if search is not None:
        conditions.append(or_(Task.title.ilike(f"%{search}%"), Task.description.ilike(f"%{search}%")))

    statement = select(Task).where(*conditions).limit(limit).offset(offset).order_by(order_by)
    total_statement = select(func.count()).select_from(Task).where(*conditions)
    tasks_manager = session.scalars(statement).all()
    total = session.scalar(total_statement)
    return tasks_manager, total

def get_client_tasks(
    session: Session,
    client_id: int
) -> list[Task]:
    statement = select(Task).where(Task.client_id == client_id)
    tasks_client = session.scalars(statement).all()
    return tasks_client

def update_task(
    session: Session,
    task_id: int,
    title: str,
    description: str,
    status: str,
    deadline: datetime
) -> bool:
    statement = select(Task).where(Task.id == task_id)
    task = session.scalars(statement).first()
    if not task:
        return False
    
    task.title = title
    task.description = description
    task.status = status
    task.deadline = deadline

    session.commit()
    return True

def delete_task(
    session: Session,
    task_id: int
) -> bool:
    statement = select(Task).where(Task.id == task_id)
    task = session.scalars(statement).first()
    if not task:
        return False

    session.delete(task)
    session.commit()
    return True

def get_all_tasks(session: Session, offset: int, limit: int):
    statement = select(Task).offset(offset).limit(limit)
    total_statement = select(func.count()).select_from(Task)

    tasks = session.scalars(statement).all()
    total = session.scalar(total_statement)
    return tasks, total