from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, func
from typing import List
from datetime import datetime
from models import Task, TimeLog, Status, User
from schemas import TaskCreate, TaskResponse, TaskUpdate
from connection import get_session

from auth import get_current_user

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=TaskResponse)
def create_task(
        task: TaskCreate,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    """Создание задачи (привязывается к текущему пользователю)"""
    db_task = Task(**task.model_dump(), user_id=current_user.id)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task


@router.get("/", response_model=List[TaskResponse])
def get_tasks(
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    """Получить задачи только текущего пользователя"""
    tasks = session.exec(select(Task).where(Task.user_id == current_user.id)).all()
    return tasks


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
        task_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    """Получить задачу по ID (только свою)"""
    task = session.get(Task, task_id)
    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(
        task_id: int,
        task_update: TaskUpdate,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    task = session.get(Task, task_id)
    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = task_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(task, key, value)

    if task.status_id == 3 and not task.completed_at:  # 3 = completed
        task.completed_at = datetime.now()

        active_logs = session.exec(
            select(TimeLog).where(
                TimeLog.task_id == task_id,
                TimeLog.end_time == None
            )
        ).all()

        for log in active_logs:
            log.end_time = datetime.now()
            log.duration_hours = (log.end_time - log.start_time).total_seconds() / 3600
            # Обновляем actual_hours задачи
            task.actual_hours += log.duration_hours
            session.add(log)

    elif task.status_id != 3 and task.completed_at:
        task.completed_at = None

    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.delete("/{task_id}")
def delete_task(
        task_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    task = session.get(Task, task_id)
    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    session.delete(task)
    session.commit()
    return {"message": "Task deleted"}
