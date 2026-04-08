from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from datetime import datetime
from models import TimeLog, Task
from schemas import TimeLogCreate, TimeLogResponse
from connection import get_session

router = APIRouter(prefix="/time-logs", tags=["time_logs"])


@router.post("/", response_model=TimeLogResponse)
def start_time_log(log: TimeLogCreate, session: Session = Depends(get_session)):
    task = session.get(Task, log.task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Проверяем активный лог
    active_log = session.exec(
        select(TimeLog).where(
            TimeLog.task_id == log.task_id,
            TimeLog.end_time == None
        )
    ).first()

    if active_log:
        raise HTTPException(status_code=400, detail="Task already has active time log")

    db_log = TimeLog(task_id=log.task_id)
    session.add(db_log)
    session.commit()
    session.refresh(db_log)
    return db_log


@router.put("/{log_id}/stop")
def stop_time_log(log_id: int, session: Session = Depends(get_session)):
    log = session.get(TimeLog, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Time log not found")

    if log.end_time:
        raise HTTPException(status_code=400, detail="Time log already stopped")

    log.end_time = datetime.now()
    log.duration_hours = (log.end_time - log.start_time).total_seconds() / 3600

    # Обновляем actual_hours задачи
    task = log.task
    task.actual_hours += log.duration_hours

    session.add(log)
    session.add(task)
    session.commit()

    return {"message": "Time log stopped", "duration_hours": log.duration_hours}


@router.get("/task/{task_id}", response_model=List[TimeLogResponse])
def get_task_time_logs(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task.time_logs