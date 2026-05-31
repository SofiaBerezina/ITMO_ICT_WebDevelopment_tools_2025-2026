from fastapi import FastAPI
from sqlmodel import select

from api import notifications, priorities, statuses, task_types, tasks, time_logs, users
from auth import get_password_hash
from connection import get_session, init_db
from models import Priority, Status, TaskType, User
from parser_client import router as parser_router

app = FastAPI(
    title="Time Manager API",
    description="API для управления временем, задачами и запуском парсера",
    version="3.0.0",
)


@app.on_event("startup")
def on_startup():
    init_db()
    init_default_data()


def init_default_data():
    """Создание базовых справочников и пользователя для данных парсера."""
    with next(get_session()) as session:
        if not session.exec(select(Priority)).first():
            session.add(Priority(name="low", level=1, color="#00FF00"))
            session.add(Priority(name="medium", level=3, color="#FFFF00"))
            session.add(Priority(name="high", level=5, color="#FF0000"))

        if not session.exec(select(Status)).first():
            session.add(Status(name="pending"))
            session.add(Status(name="in_progress"))
            session.add(Status(name="completed"))

        if not session.exec(select(TaskType)).first():
            session.add(TaskType(name="work", icon="work"))
            session.add(TaskType(name="personal", icon="home"))
            session.add(TaskType(name="study", icon="study"))

        if not session.exec(select(User).where(User.username == "parser")).first():
            session.add(
                User(
                    username="parser",
                    email="parser@example.com",
                    hashed_password=get_password_hash("parser"),
                )
            )

        session.commit()


app.include_router(users.router)
app.include_router(priorities.router)
app.include_router(statuses.router)
app.include_router(task_types.router)
app.include_router(tasks.router)
app.include_router(time_logs.router)
app.include_router(notifications.router)
app.include_router(parser_router)


@app.get("/")
def root():
    return {
        "message": "Time Manager API",
        "docs": "/docs",
        "parser_http": "/parser/parse",
        "parser_queue": "/parser/parse-async",
    }
