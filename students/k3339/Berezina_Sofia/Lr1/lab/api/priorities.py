from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from models import Priority
from schemas import PriorityResponse
from connection import get_session

router = APIRouter(prefix="/priorities", tags=["priorities"])

@router.get("/", response_model=List[PriorityResponse])
def get_priorities(session: Session = Depends(get_session)):
    """Получить список всех приоритетов"""
    priorities = session.exec(select(Priority)).all()
    return priorities

@router.get("/{priority_id}", response_model=PriorityResponse)
def get_priority(priority_id: int, session: Session = Depends(get_session)):
    """Получить приоритет по ID"""
    priority = session.get(Priority, priority_id)
    if not priority:
        raise HTTPException(status_code=404, detail="Priority not found")
    return priority