from pydantic import BaseModel, EmailStr, ConfigDict
from enums.role import Role
from enums.status import Status
from datetime import datetime
from typing import Generic, TypeVar

T = TypeVar("T")
class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    
class ClientCreate(BaseModel):
    name: str
    phone: str
    email: EmailStr | None = None

class ClientUpdate(BaseModel):
    name: str
    email: EmailStr | None = None
    phone: str

class TaskCreate(BaseModel):
    client_id: int
    title: str
    description: str
    deadline: datetime
    status: Status

class TaskUpdate(BaseModel):
    title: str
    description: str
    status: Status
    deadline: datetime

class CommentCreate(BaseModel):
    text: str

class ChangeRole(BaseModel):
    role: Role

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: Role
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ClientResponse(BaseModel):
    id: int
    name: str
    phone: str
    email: str | None
    manager_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TaskResponse(BaseModel):
    id: int
    manager_id: int
    client_id: int
    title: str
    description: str
    status: Status
    deadline: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CommentResponse(BaseModel):
    id: int
    task_id: int
    user_id: int
    text_comment: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ListResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    limit: int