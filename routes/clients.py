from fastapi import APIRouter, Depends, HTTPException, status, Query
from enums.clients import ClientSort
from enums.sort_order import SortOrder
from sqlalchemy.orm import Session
from schemas import ClientCreate, ClientResponse, ClientUpdate, ListResponse
from models import User
from dependencies import get_current_user
from data_base import get_db
from services.client_service import create_client, clients_manager, get_current_client, update_user_client, delete_user_client

router = APIRouter()

@router.post("/clients", response_model=ClientResponse, status_code=201)
def create_new_client(
    client: ClientCreate, 
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_db)
):
    name = client.name
    phone = client.phone
    email = client.email
    manager_id = current_user.id
    acces_create = create_client(session, name, phone, email, manager_id)

    return acces_create

@router.get("/clients", response_model=ListResponse[ClientResponse])
def get_clients(
    search: str | None = None,
    session: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user), 
    page: int = Query(1, ge=1), 
    limit: int = Query(20, ge=1, le=100),
    sort: ClientSort = Query(ClientSort.CREATED_AT),
    order: SortOrder = Query(SortOrder.DESC)
):
    manager_id = current_user.id
    clients = clients_manager(session, manager_id, limit, page, search, sort, order)

    return clients

@router.get("/clients/{client_id}", response_model=ClientResponse)
def get_client(
    client_id: int, 
    session: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    manager_id = current_user.id
    current_client = get_current_client(session, manager_id, client_id)
    if current_client is False:
        raise HTTPException(
            status_code=403,
            detail='Не ваш клиент'
        )
    elif current_client is None:
        raise HTTPException(
            status_code=404,
            detail='Нет такого клиента'
        )
    return current_client

@router.put("/clients/{client_id}", response_model=ClientResponse)
def update_current_client(
    client_id: int, 
    update_client: ClientUpdate, 
    session: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    manager_id = current_user.id
    acces_update = update_user_client(
        session,
        manager_id,
        client_id,
        update_client.name,
        update_client.email,
        update_client.phone
    )
    if acces_update is False:
        raise HTTPException(
            status_code=403,
            detail='Не ваш клиент'
        )
    elif acces_update is None:
        raise HTTPException(
            status_code=404,
            detail='Нет такого клиента'
        )
    
    return acces_update

@router.delete("/clients/{client_id}", status_code=204)
def delete_current_client(
    client_id: int, 
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_db)
):
    detail = 'Cannot delete client with existing tasks'
    manager_id = current_user.id
    acces_delete = delete_user_client(session, client_id, manager_id)

    if acces_delete is False:
        raise HTTPException(
            status_code=403,
            detail='Не ваш клиент'
        )
    elif acces_delete is None:
        raise HTTPException(
            status_code=404,
             detail='Нет такого клиента'
            )

    elif acces_delete == detail:
        raise HTTPException(
            status_code=409,
            detail=detail
        )
    return None