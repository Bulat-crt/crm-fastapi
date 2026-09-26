from sqlalchemy.orm import Session
from sqlalchemy import select, func
from enums.clients import ClientSort
from enums.sort_order import SortOrder
from models import Client, User

CLIENT_SORT_FIELD = {
    ClientSort.CREATED_AT: Client.created_at,
    ClientSort.NAME: Client.name
}

def create_client_db(
    session: Session,
    name: str,
    phone: str,
    email: str | None,
    manager: User
) -> Client:

    client = Client(
        name=name,
        phone=phone,
        email=email,
        manager_id=manager
    )

    session.add(client)
    session.commit()
    session.refresh(client)

    return client

def get_user_clients(
    session: Session,
    user_id: int,
    limit: int,
    offset: int,
    search: str | None,
    sort: ClientSort = ClientSort.CREATED_AT,
    order: SortOrder = SortOrder.DESC
) -> tuple[list[Client], int]:
    sort_column = CLIENT_SORT_FIELD[sort]

    if order == SortOrder.ASC:
        order_by = sort_column.asc()
    else:
        order_by = sort_column.desc()

    conditions = [Client.manager_id == user_id]
    
    if search is not None:
        conditions.append(Client.name.ilike(f"%{search}%"))
    
    statement = select(Client).where(*conditions).limit(limit).offset(offset).order_by(order_by)
    total_statement = select(func.count()).select_from(Client).where(*conditions)
    clients = session.scalars(statement).all()
    total = session.scalar(total_statement)
    return clients, total

def get_client_by_id(
    session: Session,
    client_id: int
) -> Client | None:
    statement = select(Client).where(Client.id == client_id)
    client = session.scalars(statement).first()

    return client

def update_client(
    session: Session,
    client_id: int,
    name: str,
    phone: str,
    email: str | None = None
) -> bool:
    statement = select(Client).where(Client.id == client_id)
    client = session.scalars(statement).first()
    if not client:
        return False
    client.name = name
    client.phone = phone
    client.email = email
    session.commit()
    return True

def delete_client(
    session: Session,
    client_id: int
) -> bool:
    statement = select(Client).where(Client.id == client_id)
    client = session.scalars(statement).first()
    if not client:
        return False

    session.delete(client)
    session.commit()
    return True

def get_all_clients(
    session:Session,
    offset: int,
    limit: int
):
    statement = select(Client).offset(offset).limit(limit)
    total_statement = select(func.count()).select_from(Client)
    clients = session.scalars(statement).all()
    total = session.scalar(total_statement)
    return clients, total