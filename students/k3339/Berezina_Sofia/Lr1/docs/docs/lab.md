# 🚀 Лабораторная работа 1: Тайм-менеджер на FastAPI

## Цель работы

Разработать полноценное серверное приложение тайм-менеджера с использованием FastAPI, PostgreSQL, SQLModel, Alembic и JWT-аутентификации.

---

## 📊 Модели данных (5+ таблиц)

### Схема связей

```
User (1) ────── (N) Task (1) ────── (N) TimeLog
Priority (1) ── (N) Task
Status (1) ──── (N) Task  
TaskType (1) ── (N) Task
```

### Модели

```python
# models.py

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    tasks: List["Task"] = Relationship(back_populates="user")

class Priority(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)  # low, medium, high
    level: int = Field(ge=1, le=5)
    color: str = "#888888"
    tasks: List["Task"] = Relationship(back_populates="priority")

class Status(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)  # pending, in_progress, completed
    tasks: List["Task"] = Relationship(back_populates="status")

class TaskType(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)  # work, personal, study, health
    icon: str = "📋"
    tasks: List["Task"] = Relationship(back_populates="task_type")

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = ""
    deadline: Optional[datetime] = None
    estimated_hours: float = 0.0
    actual_hours: float = 0.0
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
    priority_id: int = Field(foreign_key="priority.id")
    status_id: int = Field(foreign_key="status.id")
    task_type_id: int = Field(foreign_key="tasktype.id")
    user_id: int = Field(foreign_key="user.id")
    
    priority: Priority = Relationship(back_populates="tasks")
    status: Status = Relationship(back_populates="tasks")
    task_type: TaskType = Relationship(back_populates="tasks")
    time_logs: List["TimeLog"] = Relationship(back_populates="task")
    user: User = Relationship(back_populates="tasks")

class TimeLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="task.id")
    start_time: datetime = Field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    duration_hours: float = 0.0
    task: Task = Relationship(back_populates="time_logs")
```

### Итого: 6 таблиц

| № | Таблица | Тип связи |
|---|---------|-----------|
| 1 | User | one-to-many с Task |
| 2 | Priority | one-to-many с Task |
| 3 | Status | one-to-many с Task |
| 4 | TaskType | one-to-many с Task |
| 5 | Task | основная |
| 6 | TimeLog | many-to-one с Task |

---

## 🔌 Подключение к БД (connection.py)

```python
from sqlmodel import SQLModel, Session, create_engine

db_url = 'postgresql://postgres:123@localhost/time_manager_db'
engine = create_engine(db_url, echo=True)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
```

---

## 🔐 Аутентификация (auth.py)

```python
from datetime import datetime, timedelta
from jose import jwt
import bcrypt
from fastapi.security import HTTPBearer

SECRET_KEY = ""
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()

def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode('utf-8'), 
        hashed_password.encode('utf-8')
    )

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(credentials, session):
    token = credentials.credentials
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    user_id = int(payload.get("sub"))
    return session.get(User, user_id)
```

---

## 🌐 API Эндпоинты

### 👤 Пользователи

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| POST | `/users/register` | Регистрация |
| POST | `/users/login` | Вход, получение JWT |
| GET | `/users/me` | Информация о себе |
| GET | `/users/` | Список пользователей |
| PUT | `/users/change-password` | Смена пароля |

### 🏷️ Приоритеты (только чтение)

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| GET | `/priorities/` | Список приоритетов |
| GET | `/priorities/{id}` | Приоритет по ID |

### 📊 Статусы (только чтение)

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| GET | `/statuses/` | Список статусов |
| GET | `/statuses/{id}` | Статус по ID |

### 📂 Типы задач (полный CRUD)

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| POST | `/task-types/` | Создать тип |
| GET | `/task-types/` | Список типов |
| GET | `/task-types/{id}` | Тип по ID |
| PUT | `/task-types/{id}` | Обновить тип |
| DELETE | `/task-types/{id}` | Удалить тип |

### ✅ Задачи

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| POST | `/tasks/` | Создать задачу |
| GET | `/tasks/` | Список задач пользователя |
| GET | `/tasks/{id}` | Задача по ID |
| PATCH | `/tasks/{id}` | Обновить задачу |
| DELETE | `/tasks/{id}` | Удалить задачу |

### ⏱️ Логи времени

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| POST | `/time-logs/` | Начать учёт времени |
| PUT | `/time-logs/{log_id}/stop` | Остановить учёт |
| GET | `/time-logs/task/{task_id}` | Логи задачи |

---

## 📝 Схемы (schemas.py)

```python
# Основные схемы

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    deadline: Optional[datetime] = None
    estimated_hours: float = 0.0
    priority_id: int
    status_id: int
    task_type_id: int

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
    task_type: TaskTypeResponse  # Вложенный объект
```

---

## 🔄 Миграции Alembic

```bash
# Создание миграции
alembic revision --autogenerate -m "initial_migration"

# Применение
alembic upgrade head

# Откат
alembic downgrade -1

# Просмотр статуса
alembic current
```

---

## 🧪 Примеры запросов

### 1. Регистрация

```bash
curl -X POST "http://127.0.0.1:8000/users/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "email": "admin@example.com", "password": "123"}'
```

### 2. Логин (получение токена)

```bash
curl -X POST "http://127.0.0.1:8000/users/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "123"}'
```

### 3. Создание задачи

```bash
curl -X POST "http://127.0.0.1:8000/tasks/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <токен>" \
  -d '{"title": "Сделать лабу", "priority_id": 3, "status_id": 1, "task_type_id": 2}'
```

### 4. Начать учёт времени

```bash
curl -X POST "http://127.0.0.1:8000/time-logs/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <токен>" \
  -d '{"task_id": 1}'
```

### 5. Остановить учёт времени

```bash
curl -X PUT "http://127.0.0.1:8000/time-logs/1/stop" \
  -H "Authorization: Bearer <токен>"
```

### 6. Завершить задачу

```bash
curl -X PATCH "http://127.0.0.1:8000/tasks/1" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <токен>" \
  -d '{"status_id": 3}'
```