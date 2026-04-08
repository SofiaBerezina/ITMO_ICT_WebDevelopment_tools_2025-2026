from fastapi import FastAPI
from connection import init_db, get_session
from api import tasks, time_logs, statuses, task_types, priorities, users, notifications
from models import Priority, Status, TaskType
from sqlmodel import select

app = FastAPI(
    title="Time Manager API",
    description="API для управления временем и задачами",
    version="1.0.0"
)

@app.on_event("startup")
def on_startup():
    init_db()
    init_default_data()


def init_default_data():
    """Создание стандартных приоритетов и статусов"""
    with next(get_session()) as session:
        # Приоритеты
        if not session.exec(select(Priority)).first():
            priorities = [
                Priority(name="low", level=1, color="#00FF00"),
                Priority(name="medium", level=3, color="#FFFF00"),
                Priority(name="high", level=5, color="#FF0000"),
            ]
            for p in priorities:
                session.add(p)

        # Статусы
        if not session.exec(select(Status)).first():
            statuses = [
                Status(name="pending"),
                Status(name="in_progress"),
                Status(name="completed"),
            ]
            for s in statuses:
                session.add(s)

        # Типы задач
        if not session.exec(select(TaskType)).first():
            task_types = [
                TaskType(name="work", icon="💼"),
                TaskType(name="personal", icon="🏠"),
                TaskType(name="study", icon="📚"),
            ]
            for t in task_types:
                session.add(t)

        session.commit()

app.include_router(users.router)
app.include_router(priorities.router)
app.include_router(statuses.router)
app.include_router(task_types.router)
app.include_router(tasks.router)
app.include_router(time_logs.router)
app.include_router(notifications.router)

@app.get("/")
def root():
    return {
        "message": "Time Manager API",
        "docs": "/docs",
        "redoc": "/redoc"
    }