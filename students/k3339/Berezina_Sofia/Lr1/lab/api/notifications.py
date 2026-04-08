from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlmodel import Session, select
from models import Task, Notification, User
from connection import get_session
from auth import get_current_user

router = APIRouter(prefix="/notifications", tags=["notifications"])


def check_deadlines(session: Session, user_id: int):
    """Проверить дедлайны и создать уведомления"""

    today = datetime.now().date()
    tasks = session.exec(
        select(Task).where(
            Task.user_id == user_id,
            Task.status_id != 3,  # не завершенные
            Task.deadline.isnot(None)
        )
    ).all()

    for task in tasks:
        days_until = (task.deadline.date() - today).days

        # Проверяем, не отправляли ли уже уведомление
        existing = session.exec(
            select(Notification).where(
                Notification.task_id == task.id,
                Notification.notification_type == "deadline_reminder"
            )
        ).first()

        if existing:
            continue

        if days_until == 1:
            notification = Notification(
                user_id=user_id,
                task_id=task.id,
                notification_type="deadline_reminder",
                message=f"Задача '{task.title}' будет завтра"
            )
            session.add(notification)

        elif days_until == 0:
            notification = Notification(
                user_id=user_id,
                task_id=task.id,
                notification_type="deadline_reminder",
                message=f"Задача '{task.title}' должна быть выполнена сегодня"
            )
            session.add(notification)

        elif days_until < 0:
            notification = Notification(
                user_id=user_id,
                task_id=task.id,
                notification_type="overdue",
                message=f"Задача '{task.title}' просрочена на {abs(days_until)} дней"
            )
            session.add(notification)

    session.commit()


@router.post("/check")
def check_and_notify(
        background_tasks: BackgroundTasks,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    """Проверить дедлайны и создать уведомления"""
    background_tasks.add_task(check_deadlines, session, current_user.id)
    return {"message": "Проверка дедлайнов запущена"}


@router.get("/")
def get_notifications(
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    """Получить все уведомления пользователя"""
    notifications = session.exec(
        select(Notification).where(Notification.user_id == current_user.id)
    ).all()
    return notifications


@router.put("/{notification_id}/read")
def mark_as_read(
        notification_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    """Отметить уведомление как прочитанное"""
    notification = session.get(Notification, notification_id)
    if not notification or notification.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Notification not found")

    notification.is_read = True
    session.add(notification)
    session.commit()

    return {"message": "Notification marked as read"}


@router.delete("/{notification_id}")
def delete_notification(
        notification_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    """Удалить уведомление"""
    notification = session.get(Notification, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    if notification.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your notification")

    session.delete(notification)
    session.commit()

    return {"message": "Notification deleted"}