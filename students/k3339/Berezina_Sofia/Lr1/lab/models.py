from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str

    # Связь с задачами
    tasks: List["Task"] = Relationship(back_populates="user")

# Приоритет - one-to-many с Task
class Priority(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)  # low, medium, high
    level: int = Field(ge=1, le=5)
    color: str = "#888888"
    tasks: List["Task"] = Relationship(back_populates="priority")


# Статус - one-to-many с Task
class Status(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)  # pending, in_progress, completed
    tasks: List["Task"] = Relationship(back_populates="status")


# Тип задачи - one-to-many с Task
class TaskType(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)  # work, personal, study, health
    icon: str = "📋"
    tasks: List["Task"] = Relationship(back_populates="task_type")


# Задача
class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = ""
    deadline: Optional[datetime] = None
    estimated_hours: float = 0.0
    actual_hours: float = 0.0
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None

    # Внешние ключи
    priority_id: int = Field(foreign_key="priority.id")
    status_id: int = Field(foreign_key="status.id")
    task_type_id: int = Field(foreign_key="tasktype.id")
    user_id: int = Field(foreign_key="user.id")

    # Связи
    priority: Priority = Relationship(back_populates="tasks")
    status: Status = Relationship(back_populates="tasks")
    task_type: TaskType = Relationship(back_populates="tasks")
    time_logs: List["TimeLog"] = Relationship(back_populates="task")
    user: "User" = Relationship(back_populates="tasks")


# Лог времени - many-to-one с Task
class TimeLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="task.id")
    start_time: datetime = Field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    duration_hours: float = 0.0
    task: Task = Relationship(back_populates="time_logs")