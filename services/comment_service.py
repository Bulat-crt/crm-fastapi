from repositories.comment_repository import create_comment, get_task_comments, delete_comment, get_comment_by_id
from repositories.user_repository import get_user_by_id
from repositories.task_repository import get_task_by_id
from sqlalchemy.orm import Session

def add_comment_to_task(session: Session, task_id: int, manager_id: int, text: str):
    task = get_task_by_id(session, task_id)

    if task is None:
        return None
    
    if not task.manager_id == manager_id:
        return False


    user = get_user_by_id(session, manager_id)
    comment = create_comment(session, text, task, user)

    return comment

def get_comments_from_task(session: Session, task_id: int, manager_id: int):
    task = get_task_by_id(session, task_id)

    if task is None:
        return None
    
    if not task.manager_id == manager_id:
        return False

    comments = get_task_comments(session, task_id) 
    return comments

def delete_current_comment(session: Session, comment_id: int, manager_id: int):
    comment = get_comment_by_id(session, comment_id)

    if comment is None:
        return None

    task = get_task_by_id(session, comment.task_id)

    if not task.manager_id == manager_id:
        return False

    delete_comment(session, comment_id)

    return True