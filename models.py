#alembic revision --autogenerate -m "add user email"
#alembic upgrade head
from datetime import datetime
from enums.role import Role
from enums.status import Status
from sqlalchemy import ForeignKey, String, DateTime, func, Enum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[Role] = mapped_column(Enum(Role, native_enum=False, values_callable=lambda enum_cls: [member.value for member in enum_cls]), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    clients: Mapped[list['Client']] = relationship(back_populates='manager')
    comments: Mapped[list['Comment']] = relationship(back_populates='author')
    tasks: Mapped[list["Task"]] = relationship(back_populates="manager")

class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True)
    manager: Mapped["User"] = relationship(back_populates="clients")
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    manager_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    tasks: Mapped[list["Task"]] = relationship(back_populates='client')

class Task(Base):
    __tablename__ = 'tasks'

    id: Mapped[int] = mapped_column(primary_key=True)
    manager_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    client_id: Mapped[int] = mapped_column(ForeignKey('clients.id'), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[Status] = mapped_column(Enum(Status, native_enum=False, values_callable=lambda enum_cls: [member.value for member in enum_cls]), nullable=False)
    deadline: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    client: Mapped['Client'] = relationship(back_populates='tasks')
    comments: Mapped[list['Comment']] = relationship(back_populates='task', cascade="all, delete-orphan") 
    manager: Mapped["User"] = relationship(back_populates="tasks")

class Comment(Base):
    __tablename__ = 'comments'

    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey('tasks.id'), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    text_comment: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    task: Mapped['Task'] = relationship(back_populates='comments')
    author: Mapped['User'] = relationship(back_populates='comments')