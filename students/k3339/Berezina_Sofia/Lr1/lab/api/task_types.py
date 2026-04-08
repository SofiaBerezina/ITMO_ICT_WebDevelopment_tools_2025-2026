from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from models import TaskType
from schemas import TaskTypeCreate, TaskTypeResponse
from connection import get_session

router = APIRouter(prefix="/task-types", tags=["task_types"])

@router.post("/", response_model=TaskTypeResponse)
def create_task_type(task_type: TaskTypeCreate, session: Session = Depends(get_session)):
    db_task_type = TaskType(**task_type.model_dump())
    session.add(db_task_type)
    session.commit()
    session.refresh(db_task_type)
    return db_task_type

@router.get("/", response_model=List[TaskTypeResponse])
def get_task_types(session: Session = Depends(get_session)):
    return session.exec(select(TaskType)).all()

@router.get("/{task_type_id}", response_model=TaskTypeResponse)
def get_task_type(task_type_id: int, session: Session = Depends(get_session)):
    task_type = session.get(TaskType, task_type_id)
    if not task_type:
        raise HTTPException(status_code=404, detail="TaskType not found")
    return task_type

@router.put("/{task_type_id}", response_model=TaskTypeResponse)
def update_task_type(task_type_id: int, task_type: TaskTypeCreate, session: Session = Depends(get_session)):
    db_task_type = session.get(TaskType, task_type_id)
    if not db_task_type:
        raise HTTPException(status_code=404, detail="TaskType not found")
    for key, value in task_type.model_dump().items():
        setattr(db_task_type, key, value)
    session.add(db_task_type)
    session.commit()
    session.refresh(db_task_type)
    return db_task_type

@router.delete("/{task_type_id}")
def delete_task_type(task_type_id: int, session: Session = Depends(get_session)):
    task_type = session.get(TaskType, task_type_id)
    if not task_type:
        raise HTTPException(status_code=404, detail="TaskType not found")
    session.delete(task_type)
    session.commit()
    return {"message": "TaskType deleted"}