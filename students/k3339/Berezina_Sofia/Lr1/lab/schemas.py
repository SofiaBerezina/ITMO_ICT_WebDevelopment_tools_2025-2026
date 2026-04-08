from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True

class UserUpdatePassword(BaseModel):
    old_password: str
    new_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: int

class PriorityResponse(BaseModel):
    id: int
    name: str
    level: int
    color: str

    class Config:
        from_attributes = True

class StatusResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class TaskTypeBase(BaseModel):
    name: str
    icon: str = "📋"

class TaskTypeCreate(TaskTypeBase):
    pass

class TaskTypeResponse(TaskTypeBase):
    id: int

    class Config:
        from_attributes = True

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = ""
    deadline: Optional[datetime] = None
    estimated_hours: float = 0.0
    priority_id: int
    status_id: int
    task_type_id: int

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    priority_id: Optional[int] = None
    status_id: Optional[int] = None
    task_type_id: Optional[int] = None


class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    deadline: Optional[datetime]
    estimated_hours: float
    actual_hours: float
    created_at: datetime
    completed_at: Optional[datetime]
    priority: PriorityResponse
    status: StatusResponse
    task_type: TaskTypeResponse

    class Config:
        from_attributes = True

class TimeLogBase(BaseModel):
    task_id: int

class TimeLogCreate(TimeLogBase):
    pass

class TimeLogResponse(TimeLogBase):
    id: int
    start_time: datetime
    end_time: Optional[datetime]
    duration_hours: float

    class Config:
        from_attributes = True

class NotificationBase(BaseModel):
    task_id: int
    notification_type: str
    message: str

class NotificationCreate(NotificationBase):
    pass

class NotificationResponse(NotificationBase):
    id: int
    user_id: int
    sent_at: datetime
    is_read: bool

    class Config:
        from_attributes = True