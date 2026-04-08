from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from models import Status
from schemas import StatusResponse
from connection import get_session

router = APIRouter(prefix="/statuses", tags=["statuses"])

@router.get("/", response_model=List[StatusResponse])
def get_statuses(session: Session = Depends(get_session)):
    """Получить список всех статусов"""
    statuses = session.exec(select(Status)).all()
    return statuses

@router.get("/{status_id}", response_model=StatusResponse)
def get_status(status_id: int, session: Session = Depends(get_session)):
    """Получить статус по ID"""
    status = session.get(Status, status_id)
    if not status:
        raise HTTPException(status_code=404, detail="Status not found")
    return status