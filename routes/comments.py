from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from schemas import CommentCreate, CommentResponse
from data_base import get_db
from dependencies import get_current_user
from models import User
from services.comment_service import add_comment_to_task, get_comments_from_task, delete_current_comment

router = APIRouter()

@router.post("/tasks/{task_id}/comments", response_model=CommentResponse)
def add_comment(task_id: int, comment: CommentCreate, current_user: User = Depends(get_current_user), session: Session = Depends(get_db)):
    manager_id = current_user.id
    text = comment.text
    acces_ad = add_comment_to_task(session, task_id, manager_id, text)

    if acces_ad is False:
        raise HTTPException(
            status_code=403,
            detail='Не ваша задача'
        )

    elif acces_ad is None:
        raise HTTPException(
            status_code=404,
            detail='Нет такой задачи'
        )

    return acces_ad

@router.get("/tasks/{task_id}/comments", response_model=list[CommentResponse])
def get_comments_task(task_id: int, session: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    manager_id = current_user.id
    comments = get_comments_from_task(session, task_id, manager_id)

    if comments is False:
        raise HTTPException(
            status_code=403,
            detail='Не ваша задача'
        )

    elif comments is None:
        raise HTTPException(
            status_code=404,
            detail='Нет такой задачи'
        )

    return comments

@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(comment_id: int, session: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    manager_id = current_user.id

    acces_delete = delete_current_comment(session, comment_id, manager_id)

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