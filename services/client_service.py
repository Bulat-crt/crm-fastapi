from repositories.client_repository import create_client_db, get_user_clients, get_client_by_id, update_client, delete_client
from sqlalchemy.orm import Session
from enums.clients import ClientSort
from enums.sort_order import SortOrder
from schemas import ListResponse, ClientResponse
def create_client(
    session: Session, 
    name: str, 
    phone: str, 
    email: str | None, 
    manager_id: int
):
    client = create_client_db(session, phone, name, email, manager_id)
    return client

def clients_manager(
    session: Session,
    manager_id: int,
    limit: int,
    page: int,
    search: str | None,
    sort: ClientSort,
    order: SortOrder
) -> ListResponse[ClientResponse]:
    offset = (page - 1) * limit
    clients, total = get_user_clients(session, manager_id, limit, offset, search, sort, order)

    return ListResponse[ClientResponse](
        items=clients,
        total=total,
        page=page,
        limit=limit
    )

def get_current_client(
        session: Session,
        manager_id: int,
        client_id: int
):
    client = get_client_by_id(session, client_id)
    if client is None:
        return None

    if client.manager_id != manager_id:
        return False

    return client

def update_user_client(
    session: Session,
    manager_id: int,
    client_id: int,
    new_name: str,
    new_email: str,
    new_phone: str
):
    client = get_client_by_id(session, client_id)
    if client is None:
        return None

    if client.manager_id != manager_id:
        return False

    client = update_client(session, client_id, new_name, new_phone, new_email)
    return client

def delete_user_client(
    session: Session,
    client_id: int,
    manager_id: int
):
    client = get_client_by_id(session, client_id)
    if client is None:
        return None
    
    if client.manager_id != manager_id:
        return False

    if client.tasks:
        detail = 'Cannot delete client with existing tasks'
        return detail

    delete_client(session, client_id)
    return True