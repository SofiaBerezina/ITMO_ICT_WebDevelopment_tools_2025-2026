# Лабораторная работа 1: Тайм-менеджер на FastAPI

## Цель работы

Разработать серверное приложение тайм-менеджера с использованием фреймворка FastAPI, системы управления базами данных PostgreSQL, библиотеки SQLModel для объектно-реляционного отображения, инструмента миграций Alembic и механизма JWT-аутентификации.

---

## Модели данных

В ходе выполнения лабораторной работы было реализовано семь таблиц, что превышает требуемый минимум в пять таблиц.

### Схема связей между таблицами

- Таблица User связана с таблицей Task отношением один-ко-многим. Один пользователь может иметь множество задач.
- Таблица Priority связана с таблицей Task отношением один-ко-многим. Один приоритет может быть назначен множеству задач.
- Таблица Status связана с таблицей Task отношением один-ко-многим. Один статус может быть присвоен множеству задач.
- Таблица TaskType связана с таблицей Task отношением один-ко-многим. Один тип задачи может использоваться для множества задач.
- Таблица Task связана с таблицей TimeLog отношением один-ко-многим. Одна задача может иметь множество записей о затраченном времени.
- Таблица Notification связывает таблицы User и Task отношением многие-ко-многим. Один пользователь может иметь множество уведомлений, одна задача может порождать множество уведомлений.

### Код моделей

```python
from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    tasks: List["Task"] = Relationship(back_populates="user")
    notifications: List["Notification"] = Relationship(back_populates="user")

class Priority(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    level: int = Field(ge=1, le=5)
    color: str = "#888888"
    tasks: List["Task"] = Relationship(back_populates="priority")

class Status(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    tasks: List["Task"] = Relationship(back_populates="status")

class TaskType(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
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
    notifications: List["Notification"] = Relationship(back_populates="task")

class TimeLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="task.id")
    start_time: datetime = Field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    duration_hours: float = 0.0
    task: Task = Relationship(back_populates="time_logs")

class Notification(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    task_id: int = Field(foreign_key="task.id")
    
    notification_type: str
    sent_at: datetime = Field(default_factory=datetime.now)
    is_read: bool = False
    message: str
    
    user: User = Relationship(back_populates="notifications")
    task: Task = Relationship(back_populates="notifications")
```

### Итого: 7 таблиц

| № | Таблица | Тип связи |
|---|---------|-----------|
| 1 | User | one-to-many с Task |
| 2 | Priority | one-to-many с Task |
| 3 | Status | one-to-many с Task |
| 4 | TaskType | one-to-many с Task |
| 5 | Task | основная |
| 6 | TimeLog | many-to-one с Task |
| 7 | Notification | many-to-many между User и Task (с доп. полями) |

---

## Подключение к базе данных

Для подключения к PostgreSQL был создан файл connection.py, который содержит настройки соединения, функцию инициализации базы данных и генератор сессий.

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

## Аутентификация и авторизация

В приложении реализована JWT-аутентификация. Пароли пользователей хэшируются с использованием библиотеки bcrypt. Токен доступа действителен в течение 30 минут.

```python
from datetime import datetime, timedelta
from jose import jwt
import bcrypt
from fastapi.security import HTTPBearer

SECRET_KEY = "your-secret-key-change-in-production"
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

## API Эндпоинты

### Пользователи

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| POST | /users/register | Регистрация нового пользователя |
| POST | /users/login | Вход в систему, получение JWT токена |
| GET | /users/me | Получение информации о текущем пользователе |
| GET | /users/ | Получение списка всех пользователей |
| PUT | /users/change-password | Смена пароля |

### Приоритеты (только чтение)

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| GET | /priorities/ | Получение списка всех приоритетов |
| GET | /priorities/{id} | Получение приоритета по идентификатору |

### Статусы (только чтение)

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| GET | /statuses/ | Получение списка всех статусов |
| GET | /statuses/{id} | Получение статуса по идентификатору |

### Типы задач

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| POST | /task-types/ | Создание нового типа задачи |
| GET | /task-types/ | Получение списка всех типов задач |
| GET | /task-types/{id} | Получение типа задачи по идентификатору |
| PUT | /task-types/{id} | Полное обновление типа задачи |
| DELETE | /task-types/{id} | Удаление типа задачи |

### Задачи

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| POST | /tasks/ | Создание новой задачи |
| GET | /tasks/ | Получение списка задач текущего пользователя |
| GET | /tasks/{id} | Получение задачи по идентификатору |
| PATCH | /tasks/{id} | Частичное обновление задачи |
| DELETE | /tasks/{id} | Удаление задачи |

При обновлении статуса задачи на "completed" (status_id = 3) автоматически фиксируется время завершения задачи.

### Логи времени

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| POST | /time-logs/ | Начало учета времени на задаче |
| PUT | /time-logs/{id}/stop | Остановка учета времени |
| GET | /time-logs/task/{id} | Получение всех логов времени для задачи |

### Уведомления

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| POST | /notifications/check | Проверка дедлайнов и создание уведомлений |
| GET | /notifications/ | Получение всех уведомлений пользователя |
| PUT | /notifications/{id}/read | Отметка уведомления как прочитанного |
| DELETE | /notifications/{id} | Удаление уведомления |

Функционал уведомлений реализует дополнительную возможность, указанную в задании. При вызове эндпоинта /notifications/check система проверяет дедлайны всех незавершенных задач пользователя и создает уведомления для задач, дедлайн которых наступает сегодня, завтра или уже просрочен. Уведомления имеют тип deadline_reminder или overdue.

---

## Миграции Alembic

Для управления схемой базы данных используется Alembic. Миграции создаются автоматически на основе изменений в моделях SQLModel.

```bash
# Создание миграции
alembic revision --autogenerate -m "описание_изменений"

# Применение миграции
alembic upgrade head

# Откат последней миграции
alembic downgrade -1
```

---

## Примеры запросов к API

### Регистрация пользователя

```bash
curl -X POST "http://127.0.0.1:8000/users/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "email": "admin@example.com", "password": "123"}'
```

### Вход в систему

```bash
curl -X POST "http://127.0.0.1:8000/users/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "123"}'
```

Ответ содержит JWT токен, который необходимо использовать для авторизованных запросов.

### Создание задачи с дедлайном

```bash
curl -X POST "http://127.0.0.1:8000/tasks/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <токен>" \
  -d '{
    "title": "Сдать отчет",
    "deadline": "2026-04-10T23:59:00",
    "priority_id": 3,
    "status_id": 1,
    "task_type_id": 2
  }'
```

### Проверка дедлайнов и создание уведомлений

```bash
curl -X POST "http://127.0.0.1:8000/notifications/check" \
  -H "Authorization: Bearer <токен>"
```

Ответ:
```json
{
  "message": "Проверка дедлайнов запущена"
}
```

### Получение уведомлений

```bash
curl -X GET "http://127.0.0.1:8000/notifications/" \
  -H "Authorization: Bearer <токен>"
```

Ответ:
```json
[
  {
    "id": 1,
    "task_id": 1,
    "notification_type": "deadline_reminder",
    "message": "Задача 'Сдать отчет' будет завтра",
    "sent_at": "2026-04-09T10:00:00",
    "is_read": false
  }
]
```

### Отметка уведомления как прочитанного

```bash
curl -X PUT "http://127.0.0.1:8000/notifications/1/read" \
  -H "Authorization: Bearer <токен>"
```

---

## Вывод

В ходе выполнения лабораторной работы было разработано серверное приложение - тайм-менеджер, реализующее функционал управления задачами, учета времени и уведомлений о дедлайнах.

Были выполнены следующие задачи:

1. Спроектирована и реализована структура базы данных, состоящая из семи таблиц: User, Priority, Status, TaskType, Task, TimeLog, Notification. В модели данных реализованы связи один-ко-многим (между таблицами User, Priority, Status, TaskType и Task, а также между Task и TimeLog) и многие-ко-многим (между User и Task через ассоциативную таблицу Notification).

2. Ассоциативная сущность Notification имеет дополнительные поля, характеризующие связь: notification_type (тип уведомления), sent_at (время отправки), is_read (статус прочтения) и message (текст уведомления). Это полностью соответствует требованию о наличии дополнительного поля в ассоциативной сущности.

3. Реализован CRUD API для работы с задачами, типами задач, пользователями и уведомлениями. GET-запросы возвращают вложенные объекты, что позволяет клиентскому приложению получать полную информацию о задаче вместе с её приоритетом, статусом и типом за один запрос.

4. Реализована дополнительная функция, указанная в задании - уведомления о приближении к дедлайнам. При вызове соответствующего эндпоинта система проверяет дедлайны задач и создает уведомления для задач, требующих внимания.

5. Настроена система миграций Alembic, которая позволяет отслеживать изменения в структуре базы данных и применять их последовательно.

6. Реализована JWT-аутентификация с хэшированием паролей с использованием bcrypt, что обеспечивает безопасное хранение учетных данных и защиту API-эндпоинтов.

7. Создана документация API с помощью встроенного инструмента FastAPI - Swagger UI, доступная по адресу /docs.

В результате проделанной работы получено полноценное серверное приложение, соответствующее всем требованиям лабораторной работы. Приложение позволяет пользователям регистрироваться, создавать задачи, отслеживать их выполнение, учитывать затраченное время и получать уведомления о приближающихся дедлайнах.
