from sqlalchemy import select
from sqlalchemy.orm import Session

from models import Task, User, Comment


def create_comment(
    session: Session,
    text: str,
    task: Task,
    author: User
) -> Comment:

    comment = Comment(
        text_comment = text,
        task_id = task.id,
        author = author
    )

    session.add(comment)
    session.commit()
    session.refresh(comment)

    return comment


def get_task_comments(
    session: Session,
    task_id: int
) -> list[Comment]:
    statement = select(Comment).where(Comment.task_id == task_id)
    comments = session.scalars(statement).all()
    return comments

def get_comment_by_id(
    session: Session,
    comment_id: int
) -> Comment:
    statement = select(Comment).where(Comment.id == comment_id)
    comment = session.scalars(statement).first()
    return comment

def delete_comment(
    session: Session,
    comment_id: int
) -> bool:
    statement = select(Comment).where(Comment.id == comment_id)
    comment = session.scalars(statement).first()
    if not comment:
        return False

    session.delete(comment)
    session.commit()
    return True